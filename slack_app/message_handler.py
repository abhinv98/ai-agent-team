import asyncio
import logging
import json
import re

from slack_sdk import WebClient

from orchestrator.db import get_supabase
from orchestrator.task_router import create_tasks_for_campaign, get_unblocked_tasks, trigger_agent_for_task
from orchestrator.workflow_engine import WORKFLOW_TEMPLATES, detect_workflow_type
from orchestrator.cost_tracker import get_daily_cost
from slack_app.channel_config import AGENT_DISPLAY, CHANNEL
from slack_app.approval_handler import post_for_approval, _upload_full_output

logger = logging.getLogger(__name__)

LONG_RESPONSE_LIMIT = 2800

_agents_cache = {}

AGENT_KEYWORDS = {
    "maya": [
        "campaign", "strategy", "plan", "launch", "pricing", "positioning",
        "marketing ideas", "brand", "audience", "go-to-market", "gtm",
        "competitor", "market", "roadmap",
    ],
    "ananya": [
        "write", "copy", "blog", "email", "headline", "landing page",
        "newsletter", "content", "subject line", "cta", "call to action",
        "ad copy", "tagline", "rewrite", "draft",
    ],
    "priya": [
        "seo", "keyword", "ranking", "traffic", "backlink", "schema",
        "sitemap", "indexing", "research", "info", "gathering", "search",
        "crawl", "meta description", "core web vitals", "serp",
    ],
    "ramesh": [
        "social", "linkedin", "twitter", "instagram", "tiktok", "post",
        "calendar", "hashtag", "ad creative", "reel", "carousel", "thread",
        "engagement", "hook", "social media",
    ],
    "subodh": [
        "analytics", "data", "metrics", "a/b test", "conversion rate",
        "roas", "cpa", "report", "performance", "trends", "news",
        "tracking", "ga4", "attribution", "cpm", "ctr", "cpc",
        "paid ads", "budget allocation",
    ],
    "kavya": [
        "standup", "status", "cost", "budget", "progress", "tasks",
        "blockers", "update",
    ],
}


def _route_to_agent(text: str) -> str:
    """Match message text to the best agent using keyword scoring."""
    text_lower = text.lower()
    scores = {}
    for agent_name, keywords in AGENT_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text_lower:
                score += len(kw)
        scores[agent_name] = score

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "maya"
    return best


def _get_agent(name: str):
    """Lazily instantiate and cache agent by name."""
    if name in _agents_cache:
        return _agents_cache[name]

    from agents import (
        MayaStrategist, AnanyaCopywriter, PriyaSEO,
        RameshSocial, SubodhAnalyst, KavyaPM,
    )
    agent_map = {
        "maya": MayaStrategist,
        "ananya": AnanyaCopywriter,
        "priya": PriyaSEO,
        "ramesh": RameshSocial,
        "subodh": SubodhAnalyst,
        "kavya": KavyaPM,
    }
    cls = agent_map.get(name)
    if not cls:
        return None
    _agents_cache[name] = cls()
    return _agents_cache[name]


def handle_channel_message(event, client: WebClient):
    """Handle normal messages in the channel -- route to the right agent."""
    if event.get("bot_id") or event.get("subtype"):
        return

    text = event.get("text", "").strip()
    channel = event.get("channel")
    thread_ts = event.get("ts")

    if not text:
        return

    from orchestrator.killswitch import is_paused
    if is_paused():
        client.chat_postMessage(
            channel=channel,
            text="Agents are currently paused. Resume from the dashboard to continue.",
            thread_ts=thread_ts,
        )
        return

    agent_name = _route_to_agent(text)
    display = AGENT_DISPLAY.get(agent_name, {"name": agent_name})

    client.chat_postMessage(
        channel=channel,
        text=f"{display['name']} is looking into this...",
        thread_ts=thread_ts,
    )

    agent = _get_agent(agent_name)
    if not agent:
        client.chat_postMessage(
            channel=channel,
            text="Could not find the right agent. Please try again.",
            thread_ts=thread_ts,
        )
        return

    result = agent.call(user_message=text)
    response_text = result.get("text", "I couldn't generate a response.")

    if len(response_text) > LONG_RESPONSE_LIMIT:
        preview = response_text[:LONG_RESPONSE_LIMIT] + "\n\n_...full response attached as file._"
        client.chat_postMessage(channel=channel, text=preview, thread_ts=thread_ts)
        _upload_full_output(client, CHANNEL, f"Response from {display['name']}", response_text, thread_ts=thread_ts)
    else:
        client.chat_postMessage(channel=channel, text=response_text, thread_ts=thread_ts)


def handle_app_mention(event, client: WebClient):
    """Route @mentions to the appropriate agent based on message content."""
    text = event.get("text", "").strip()
    text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
    channel = event.get("channel")
    thread_ts = event.get("ts")

    if not text:
        client.chat_postMessage(
            channel=channel,
            text="How can I help? Ask a marketing question or use `/campaign <brief>` to start a campaign.",
            thread_ts=thread_ts,
        )
        return

    campaign_triggers = ["campaign", "launch campaign", "new campaign", "plan campaign", "start campaign"]
    if any(trigger in text.lower() for trigger in campaign_triggers):
        client.chat_postMessage(
            channel=channel,
            text="Maya is analyzing your campaign brief...",
            thread_ts=thread_ts,
        )
        _run_async(_launch_campaign(text, channel, client))
        return

    from orchestrator.killswitch import is_paused
    if is_paused():
        client.chat_postMessage(
            channel=channel,
            text="Agents are currently paused. Resume from the dashboard to continue.",
            thread_ts=thread_ts,
        )
        return

    agent_name = _route_to_agent(text)
    display = AGENT_DISPLAY.get(agent_name, {"name": agent_name})

    client.chat_postMessage(
        channel=channel,
        text=f"{display['name']} is looking into this...",
        thread_ts=thread_ts,
    )

    agent = _get_agent(agent_name)
    if not agent:
        return

    result = agent.call(user_message=text)
    response_text = result.get("text", "I couldn't generate a response.")

    if len(response_text) > LONG_RESPONSE_LIMIT:
        preview = response_text[:LONG_RESPONSE_LIMIT] + "\n\n_...full response attached as file._"
        client.chat_postMessage(channel=channel, text=preview, thread_ts=thread_ts)
        _upload_full_output(client, CHANNEL, f"Response from {display['name']}", response_text, thread_ts=thread_ts)
    else:
        client.chat_postMessage(channel=channel, text=response_text, thread_ts=thread_ts)


def handle_campaign_command(ack, command, client: WebClient):
    """Handle /campaign slash command."""
    ack()
    brief = command.get("text", "").strip()
    if not brief:
        client.chat_postMessage(
            channel=command["channel_id"],
            text="Usage: `/campaign <brief>` -- e.g. `/campaign Launch a blog series about AI in healthcare`",
        )
        return

    client.chat_postMessage(
        channel=command["channel_id"],
        text="Starting new campaign -- Maya is analyzing the brief.",
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
        display = AGENT_DISPLAY.get(c["agent_name"], {"name": c["agent_name"]})
        lines.append(f"  {display['name']}: ${c['cost']:.4f} ({c['calls']} calls)")

    text = f"*Today's API Costs: ${total:.4f}*\n\n" + "\n".join(lines)
    client.chat_postMessage(channel=command["channel_id"], text=text)


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

    maya = _get_agent("maya")
    plan_result = maya.plan_campaign(brief, campaign_id=campaign_id)
    plan_text = plan_result.get("text", "")

    client.chat_postMessage(
        channel=CHANNEL,
        text=f"*Maya's Campaign Plan*\n\n{plan_text[:3000]}",
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
