import json
import logging
import asyncio
import re
import threading

from slack_sdk import WebClient

from slack_app.channel_config import CHANNEL, AGENT_DISPLAY
from orchestrator.task_router import update_task, get_task, process_approved_task
from orchestrator.knowledge_base import store_approved_output

logger = logging.getLogger(__name__)

PREVIEW_CHAR_LIMIT = 2400

_channel_id_cache = {}


def _resolve_channel_id(client: WebClient, channel_name: str) -> str:
    """Resolve #channel-name to a Slack channel ID (cached)."""
    if channel_name in _channel_id_cache:
        return _channel_id_cache[channel_name]

    clean = channel_name.lstrip("#")
    try:
        cursor = None
        while True:
            resp = client.conversations_list(
                types="public_channel,private_channel",
                limit=200,
                cursor=cursor,
            )
            for ch in resp.get("channels", []):
                if ch["name"] == clean:
                    _channel_id_cache[channel_name] = ch["id"]
                    return ch["id"]
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
    except Exception as e:
        logger.error("Failed to resolve channel ID for %s: %s", channel_name, e)

    return channel_name


def _upload_full_output(client: WebClient, channel: str, title: str, content: str, thread_ts: str = None):
    """Upload the full agent output as a text file in the thread."""
    channel_id = _resolve_channel_id(client, channel)
    try:
        kwargs = {
            "channel": channel_id,
            "title": f"{title}.txt",
            "content": content,
            "filename": f"{title[:50]}.txt",
            "filetype": "text",
        }
        if thread_ts:
            kwargs["thread_ts"] = thread_ts
        client.files_upload_v2(**kwargs)
    except Exception as e:
        logger.error("Failed to upload file for %s: %s", title, e)


def _parse_to_rich_text(text: str) -> list[dict]:
    """Convert agent output to Slack rich_text block elements (sections + bullet lists)."""
    if not text:
        return [{"type": "rich_text_section", "elements": [{"type": "text", "text": "No content generated."}]}]

    clean = text.replace("**", "").replace("__", "")
    clean = re.sub(r"#{1,4}\s*", "", clean)
    clean = re.sub(r"\|.*?\|", "", clean)

    lines = clean.split("\n")
    elements = []
    bullet_buffer = []

    def flush_bullets():
        if not bullet_buffer:
            return
        items = []
        for b in bullet_buffer:
            items.append({
                "type": "rich_text_section",
                "elements": [{"type": "text", "text": b.strip()}],
            })
        elements.append({"type": "rich_text_list", "style": "bullet", "elements": items})
        bullet_buffer.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_bullets()
            continue

        is_bullet = bool(re.match(r"^[-*]\s+", stripped)) or bool(re.match(r"^\d+[\.\)]\s+", stripped))

        if is_bullet:
            clean_bullet = re.sub(r"^[-*]\s+", "", stripped)
            clean_bullet = re.sub(r"^\d+[\.\)]\s+", "", clean_bullet)
            bullet_buffer.append(clean_bullet)
        else:
            flush_bullets()

            if stripped.endswith(":") or len(stripped) < 80 and not stripped.endswith("."):
                elements.append({
                    "type": "rich_text_section",
                    "elements": [{"type": "text", "text": stripped, "style": {"bold": True}}],
                })
            else:
                elements.append({
                    "type": "rich_text_section",
                    "elements": [{"type": "text", "text": stripped}],
                })

    flush_bullets()

    total_chars = sum(
        sum(len(el.get("text", "")) for el in elem.get("elements", []))
        for elem in elements
    )
    if total_chars > PREVIEW_CHAR_LIMIT:
        trimmed = []
        chars = 0
        for elem in elements:
            elem_chars = sum(len(el.get("text", "")) for el in elem.get("elements", []))
            if chars + elem_chars > PREVIEW_CHAR_LIMIT:
                trimmed.append({
                    "type": "rich_text_section",
                    "elements": [{"type": "text", "text": "\n...content truncated. Full output attached as file.", "style": {"italic": True}}],
                })
                break
            trimmed.append(elem)
            chars += elem_chars
        elements = trimmed

    return elements or [{"type": "rich_text_section", "elements": [{"type": "text", "text": text[:2400]}]}]


def post_for_approval(client: WebClient, task: dict):
    """Post agent output with approval buttons. Always uploads full content as file."""
    agent_name = task["assigned_agent"]
    display = AGENT_DISPLAY.get(agent_name, {"name": agent_name, "color": "#666"})
    output = task.get("output_content", "No content generated.")
    task_payload = json.dumps({"task_id": task["id"], "agent": agent_name})

    rich_elements = _parse_to_rich_text(output)

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": task["title"][:150]}},
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"*{display['name']}*  |  Awaiting review"},
            ],
        },
        {"type": "divider"},
        {"type": "rich_text", "elements": rich_elements},
        {"type": "divider"},
        {
            "type": "actions",
            "block_id": f"approval_{task['id']}",
            "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": "Approve"}, "style": "primary", "action_id": "approve_task", "value": task_payload},
                {"type": "button", "text": {"type": "plain_text", "text": "Request Changes"}, "action_id": "request_changes", "value": task_payload},
                {"type": "button", "text": {"type": "plain_text", "text": "Reject"}, "style": "danger", "action_id": "reject_task", "value": task_payload},
            ],
        },
    ]

    try:
        result = client.chat_postMessage(
            channel=CHANNEL,
            text=f"{display['name']} completed: {task['title']}",
            blocks=blocks,
        )
        msg_ts = result.get("ts")
        if msg_ts:
            update_task(task["id"], {"slack_message_ts": msg_ts, "slack_channel": CHANNEL})
            _upload_full_output(client, CHANNEL, task["title"], output, thread_ts=msg_ts)

    except Exception as e:
        logger.error("Failed to post approval to %s: %s — trying fallback", CHANNEL, e)
        _post_fallback(client, task, display, task_payload, output)


def _post_fallback(client: WebClient, task: dict, display: dict, task_payload: str, output: str):
    """Fallback: minimal message + full output as file."""
    try:
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": task["title"][:150]}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": f"*{display['name']}*  |  Awaiting review"}]},
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "_Full output attached as file in thread._"}},
            {"type": "divider"},
            {
                "type": "actions",
                "block_id": f"approval_{task['id']}",
                "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "Approve"}, "style": "primary", "action_id": "approve_task", "value": task_payload},
                    {"type": "button", "text": {"type": "plain_text", "text": "Request Changes"}, "action_id": "request_changes", "value": task_payload},
                    {"type": "button", "text": {"type": "plain_text", "text": "Reject"}, "style": "danger", "action_id": "reject_task", "value": task_payload},
                ],
            },
        ]

        result = client.chat_postMessage(channel=CHANNEL, text=f"{display['name']} completed: {task['title']}", blocks=blocks)
        msg_ts = result.get("ts")
        if msg_ts:
            update_task(task["id"], {"slack_message_ts": msg_ts, "slack_channel": CHANNEL})
            _upload_full_output(client, CHANNEL, task["title"], output, thread_ts=msg_ts)

    except Exception as e:
        logger.error("Fallback post also failed for task %s: %s", task.get("id"), e)


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
        text=f"*{task['title']}* -- approved by @{user}",
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
            "blocks": [{
                "type": "input",
                "block_id": "feedback_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "feedback_input",
                    "multiline": True,
                    "placeholder": {"type": "plain_text", "text": "What changes are needed?"},
                },
                "label": {"type": "plain_text", "text": "Feedback"},
            }],
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

    display = AGENT_DISPLAY.get(agent_name, {"name": agent_name})
    client.chat_postMessage(
        channel=CHANNEL,
        text=f"Changes requested for *{task['title']}*:\n> {feedback}\n\n{display['name']} is working on revisions...",
    )

    thread = threading.Thread(
        target=_run_revision,
        args=(client, task, agent_name, feedback),
        daemon=True,
    )
    thread.start()


def _run_revision(client: WebClient, task: dict, agent_name: str, feedback: str):
    """Run the agent revision in a background thread so the Slack handler doesn't block."""
    task_id = task["id"]
    display = AGENT_DISPLAY.get(agent_name, {"name": agent_name})

    try:
        from orchestrator.killswitch import is_paused
        if is_paused():
            client.chat_postMessage(
                channel=CHANNEL,
                text=f"Agents are currently paused. {display['name']} cannot revise right now. Resume from the dashboard to continue.",
            )
            return

        from orchestrator.task_router import get_agent
        agent = get_agent(agent_name)
        if not agent:
            logger.error("No agent found for revision: %s", agent_name)
            client.chat_postMessage(
                channel=CHANNEL,
                text=f"Could not find agent '{agent_name}' to process revisions.",
            )
            return

        if agent_name == "ananya":
            result = agent.revise_content(
                original=task.get("output_content", ""),
                feedback=feedback,
                task_id=task_id,
                campaign_id=task.get("campaign_id"),
            )
        else:
            result = agent.call(
                user_message=(
                    f"Revise your previous output based on this feedback. "
                    f"Return the complete revised version:\n\n"
                    f"<original>\n{task.get('output_content', '')[:3000]}\n</original>\n\n"
                    f"<feedback>\n{feedback}\n</feedback>"
                ),
                task_id=task_id,
                campaign_id=task.get("campaign_id"),
            )

        revised_text = result.get("text", "")
        if not revised_text or revised_text.startswith("[Paused]"):
            client.chat_postMessage(
                channel=CHANNEL,
                text=f"{display['name']} could not complete the revision. Agents may be paused.",
            )
            return

        update_task(task_id, {"status": "pending_review", "output_content": revised_text})
        updated_task = {**task, "output_content": revised_text, "status": "pending_review"}
        post_for_approval(client, updated_task)
        logger.info("Revision posted for task %s by agent %s", task_id, agent_name)

    except Exception as e:
        logger.error("Revision failed for task %s (agent %s): %s", task_id, agent_name, e, exc_info=True)
        try:
            client.chat_postMessage(
                channel=CHANNEL,
                text=f"Revision failed for *{task.get('title', task_id)}*. {display['name']} encountered an error. Please try again.",
            )
        except Exception:
            logger.error("Could not post revision failure message to Slack")


def handle_reject(ack, body, client):
    ack()
    payload = json.loads(body["actions"][0]["value"])
    task_id = payload["task_id"]
    user = body["user"]["username"]

    task = get_task(task_id)
    title = task["title"] if task else task_id
    update_task(task_id, {"status": "done", "feedback": f"Rejected by {user}"})
    client.chat_postMessage(channel=CHANNEL, text=f"*{title}* -- rejected by @{user}")


def _store_to_knowledge(task: dict, approved_by: str):
    if not task.get("output_content"):
        return
    try:
        feedback_history = []
        if task.get("feedback"):
            feedback_history.append({"feedback": task["feedback"], "revision": "applied"})
        store_approved_output(
            agent_name=task["assigned_agent"], category=_infer_category(task),
            topic=task.get("title", ""), approved_output=task["output_content"],
            task_id=task["id"], campaign_id=task.get("campaign_id"),
            input_context=task.get("description", ""), feedback_history=feedback_history,
            tags=_extract_tags(task), approved_by=approved_by,
        )
    except Exception as e:
        logger.error("Failed to store knowledge: %s", e)


def _infer_category(task: dict) -> str:
    agent = task.get("assigned_agent", "")
    title = task.get("title", "").lower()
    return {"priya": "keyword_brief", "ananya": "blog_post" if "blog" in title else "content",
            "ramesh": "social_calendar", "subodh": "analysis", "maya": "campaign_plan", "kavya": "standup"}.get(agent, "general")


def _extract_tags(task: dict) -> list[str]:
    tags = [task.get("assigned_agent", "")]
    tags.extend([w for w in task.get("title", "").lower().split() if len(w) > 3][:5])
    return tags
