import os
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logger = logging.getLogger(__name__)

_app = None


def get_app() -> App:
    global _app
    if _app is not None:
        return _app

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

    _app = App(
        token=os.environ.get("SLACK_BOT_TOKEN", ""),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET", ""),
    )

    _app.command("/campaign")(handle_campaign_command)
    _app.command("/standup")(handle_standup_command)
    _app.command("/costs")(handle_costs_command)

    _app.action("approve_task")(handle_approve)
    _app.action("request_changes")(handle_request_changes)
    _app.action("reject_task")(handle_reject)

    _app.view("feedback_modal")(handle_feedback_submission)

    _app.event("app_mention")(handle_app_mention)

    @_app.event("message")
    def handle_message_events(body, logger):
        pass

    return _app


def start_slack_bot():
    logger.info("Starting Slack bot in Socket Mode...")
    app = get_app()
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN", ""))
    handler.start()
