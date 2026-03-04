import os
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_app.approval_handler import (
    handle_approve,
    handle_request_changes,
    handle_reject,
    handle_feedback_submission,
)
from slack_app.message_handler import (
    handle_campaign_command,
    handle_standup_command,
    handle_costs_command,
    handle_app_mention,
)

logger = logging.getLogger(__name__)

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)

# ── Slash commands ──
app.command("/campaign")(handle_campaign_command)
app.command("/standup")(handle_standup_command)
app.command("/costs")(handle_costs_command)

# ── Approval actions ──
app.action("approve_task")(handle_approve)
app.action("request_changes")(handle_request_changes)
app.action("reject_task")(handle_reject)

# ── Modal submissions ──
app.view("feedback_modal")(handle_feedback_submission)

# ── Events ──
app.event("app_mention")(handle_app_mention)


@app.event("message")
def handle_message_events(body, logger):
    """Acknowledge message events to prevent Slack warnings."""
    pass


def start_slack_bot():
    logger.info("Starting Slack bot in Socket Mode...")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
