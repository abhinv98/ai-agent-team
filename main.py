import logging
import threading
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

from slack_app.bot import start_slack_bot
from dashboard.api.main import app as fastapi_app
import uvicorn


def run_api():
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=int(os.environ.get("API_PORT", 8000)),
        log_level="info",
    )


if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    logging.info("FastAPI server started on port %s", os.environ.get("API_PORT", 8000))

    logging.info("Starting Slack bot...")
    start_slack_bot()
