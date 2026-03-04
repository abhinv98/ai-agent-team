import asyncio
import logging
import json

from slack_sdk import WebClient

from agents import MayaStrategist
from agents.base_agent import get_supabase
from orchestrator.task_router import create_tasks_for_campaign, get_unblocked_tasks, trigger_agent_for_task
from orchestrator.workflow_engine import WORKFLOW_TEMPLATES, detect_workflow_type
from orchestrator.cost_tracker import get_daily_cost
from slack_app.channel_config import AGENT_DISPLAY, CHANNEL
from slack_app.approval_handler import post_for_approval

logger = logging.getLogger(__name__)

maya = MayaStrategist()


def handle_campaign_command(ack, command, client: WebClient):
    """Handle /campaign slash command."""
    ack()
    brief = command.get("text", "").strip()
    if not brief:
        client.chat_postMessage(
            channel=command["channel_id"],
            text="Usage: `/campaign <brief>` — e.g. `/campaign Launch a blog series about AI in healthcare`",
        )
        return

    client.chat_postMessage(
        channel=command["channel_id"],
        text=f"🎯 Starting new campaign... Maya is analyzing the brief.",
    )

    _run_async(_launch_campaign(brief, command["channel_id"], client))


def handle_standup_command(ack, command, client: WebClient):
    """Handle /standup slash command."""
    ack()
    from agents import KavyaPM
    from orchestrator.task_router import _build_tasks_summary

    kavya = KavyaPM()
    db = get_supabase()
    campaigns = db.table("campaigns").select("id").eq("status", "active").execute().data or []

    result = kavya.generate_standup(
        tasks_summary=_build_tasks_summary(),
        campaign_count=len(campaigns),
    )

    client.chat_postMessage(
        channel=command["channel_id"],
        text=result.get("text", "No standup data available."),
    )


def handle_costs_command(ack, command, client: WebClient):
    """Handle /costs slash command."""
    ack()
    costs = get_daily_cost()
    if not costs:
        client.chat_postMessage(channel=command["channel_id"], text="No API costs recorded today.")
        return

    total = sum(c["cost"] for c in costs)
    lines = []
    for c in sorted(costs, key=lambda x: x["cost"], reverse=True):
        display = AGENT_DISPLAY.get(c["agent_name"], {"emoji": "🤖", "name": c["agent_name"]})
        lines.append(f"{display['emoji']} {display['name']}: ${c['cost']:.4f} ({c['calls']} calls)")

    text = f"💰 *Today's API Costs: ${total:.4f}*\n\n" + "\n".join(lines)
    client.chat_postMessage(channel=command["channel_id"], text=text)


def handle_app_mention(event, client: WebClient):
    """Route @mentions to the appropriate agent."""
    text = event.get("text", "").strip()
    channel = event.get("channel")

    client.chat_postMessage(
        channel=channel,
        text="🎯 Maya is reviewing your brief...",
        thread_ts=event.get("ts"),
    )

    _run_async(_launch_campaign(text, channel, client))


async def _launch_campaign(brief: str, channel: str, client: WebClient):
    """Create campaign, get Maya's plan, create tasks, post for approval."""
    db = get_supabase()

    campaign_result = db.table("campaigns").insert({
        "name": brief[:100],
        "brief": brief,
        "status": "active",
    }).execute()
    campaign = campaign_result.data[0]
    campaign_id = campaign["id"]

    plan_result = maya.plan_campaign(brief, campaign_id=campaign_id)
    plan_text = plan_result.get("text", "")

    client.chat_postMessage(
        channel=CHANNEL,
        text=f"🎯 *Maya's Campaign Plan*\n\n{plan_text[:3000]}",
    )

    workflow_type = detect_workflow_type(brief)
    template_fn = WORKFLOW_TEMPLATES.get(workflow_type, WORKFLOW_TEMPLATES["blog"])
    task_defs = template_fn(campaign_id, brief)
    created_tasks = create_tasks_for_campaign(campaign_id, task_defs)

    plan_task = {
        "id": created_tasks[0]["id"] if created_tasks else "plan",
        "title": f"Campaign Plan: {brief[:60]}",
        "assigned_agent": "maya",
        "output_content": plan_text,
        "campaign_id": campaign_id,
        "status": "pending_review",
        "slack_message_ts": None,
        "slack_channel": None,
        "description": brief,
        "feedback": None,
    }
    post_for_approval(client, plan_task)

    return campaign_id


def _run_async(coro):
    """Run an async coroutine from sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(coro)
        else:
            loop.run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(coro)
        finally:
            loop.close()
