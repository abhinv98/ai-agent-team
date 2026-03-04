import json
import logging
import asyncio

from slack_sdk import WebClient

from slack_app.channel_config import CHANNEL, AGENT_DISPLAY
from orchestrator.task_router import update_task, get_task, process_approved_task
from orchestrator.knowledge_base import store_approved_output

logger = logging.getLogger(__name__)


def post_for_approval(client: WebClient, task: dict):
    """Post agent output with approval buttons in the single channel."""
    agent_name = task["assigned_agent"]
    display = AGENT_DISPLAY.get(agent_name, {"name": agent_name, "emoji": "🤖"})
    output = task.get("output_content", "No content generated.")
    preview = output[:2000] + ("..." if len(output) > 2000 else "")
    task_payload = json.dumps({"task_id": task["id"], "agent": agent_name})

    try:
        result = client.chat_postMessage(
            channel=CHANNEL,
            text=f"{display['emoji']} {display['name']} completed: {task['title']}",
            blocks=[
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"{display['emoji']} {task['title']}"},
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Agent:* {display['emoji']} {display['name']}\n\n{preview}",
                    },
                },
                {"type": "divider"},
                {
                    "type": "actions",
                    "block_id": f"approval_{task['id']}",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "✅ Approve"},
                            "style": "primary",
                            "action_id": "approve_task",
                            "value": task_payload,
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "✏️ Request Changes"},
                            "action_id": "request_changes",
                            "value": task_payload,
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "❌ Reject"},
                            "style": "danger",
                            "action_id": "reject_task",
                            "value": task_payload,
                        },
                    ],
                },
            ],
        )
        if result.get("ts"):
            update_task(task["id"], {"slack_message_ts": result["ts"], "slack_channel": CHANNEL})
    except Exception as e:
        logger.error("Failed to post approval to %s: %s", CHANNEL, e)


def handle_approve(ack, body, client):
    ack()
    payload = json.loads(body["actions"][0]["value"])
    task_id = payload["task_id"]
    user = body["user"]["username"]

    task = get_task(task_id)
    if not task:
        return

    update_task(task_id, {"status": "approved", "approved_by": user})
    _store_to_knowledge(task, user)

    client.chat_postMessage(
        channel=CHANNEL,
        text=f"✅ *{task['title']}* approved by @{user}",
        thread_ts=task.get("slack_message_ts"),
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process_approved_task(task_id))
    finally:
        loop.close()


def handle_request_changes(ack, body, client):
    ack()
    payload = json.loads(body["actions"][0]["value"])

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "feedback_modal",
            "private_metadata": json.dumps(payload),
            "title": {"type": "plain_text", "text": "Request Changes"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "feedback_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "feedback_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "What changes are needed?"},
                    },
                    "label": {"type": "plain_text", "text": "Feedback"},
                },
            ],
        },
    )


def handle_feedback_submission(ack, body, client):
    ack()
    payload = json.loads(body["view"]["private_metadata"])
    task_id = payload["task_id"]
    agent_name = payload["agent"]
    feedback = body["view"]["state"]["values"]["feedback_block"]["feedback_input"]["value"]

    task = get_task(task_id)
    if not task:
        return

    update_task(task_id, {"status": "changes_requested", "feedback": feedback})

    client.chat_postMessage(
        channel=CHANNEL,
        text=f"✏️ Changes requested for *{task['title']}*: {feedback}",
    )

    from orchestrator.task_router import get_agent
    agent = get_agent(agent_name)
    if agent and agent_name == "ananya":
        result = agent.revise_content(
            original=task.get("output_content", ""),
            feedback=feedback,
            task_id=task_id,
            campaign_id=task.get("campaign_id"),
        )
        update_task(task_id, {"status": "pending_review", "output_content": result.get("text", "")})
        post_for_approval(client, {**task, "output_content": result.get("text", ""), "status": "pending_review"})
    elif agent:
        result = agent.call(
            user_message=f"Revise based on feedback:\n\nOriginal: {task.get('output_content', '')[:3000]}\n\nFeedback: {feedback}",
            task_id=task_id,
            campaign_id=task.get("campaign_id"),
        )
        update_task(task_id, {"status": "pending_review", "output_content": result.get("text", "")})
        post_for_approval(client, {**task, "output_content": result.get("text", ""), "status": "pending_review"})


def handle_reject(ack, body, client):
    ack()
    payload = json.loads(body["actions"][0]["value"])
    task_id = payload["task_id"]
    user = body["user"]["username"]

    update_task(task_id, {"status": "done", "feedback": f"Rejected by {user}"})

    client.chat_postMessage(
        channel=CHANNEL,
        text=f"❌ *{payload.get('task_id', 'Task')}* rejected by @{user}",
    )


def _store_to_knowledge(task: dict, approved_by: str):
    if not task.get("output_content"):
        return
    try:
        feedback_history = []
        if task.get("feedback"):
            feedback_history.append({"feedback": task["feedback"], "revision": "applied"})

        store_approved_output(
            agent_name=task["assigned_agent"],
            category=_infer_category(task),
            topic=task.get("title", ""),
            approved_output=task["output_content"],
            task_id=task["id"],
            campaign_id=task.get("campaign_id"),
            input_context=task.get("description", ""),
            feedback_history=feedback_history,
            tags=_extract_tags(task),
            approved_by=approved_by,
        )
    except Exception as e:
        logger.error("Failed to store knowledge: %s", e)


def _infer_category(task: dict) -> str:
    agent = task.get("assigned_agent", "")
    title = task.get("title", "").lower()
    mapping = {
        "priya": "keyword_brief",
        "ananya": "blog_post" if "blog" in title else "newsletter" if "newsletter" in title else "content",
        "ramesh": "social_calendar",
        "subodh": "analysis",
        "maya": "campaign_plan",
        "kavya": "standup",
    }
    return mapping.get(agent, "general")


def _extract_tags(task: dict) -> list[str]:
    tags = [task.get("assigned_agent", "")]
    title_words = task.get("title", "").lower().split()
    tags.extend([w for w in title_words if len(w) > 3][:5])
    return tags
