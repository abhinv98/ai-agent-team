"""Global kill switch to pause/resume all agent work. In-memory for speed."""
import logging
import threading

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_paused = False


def is_paused() -> bool:
    with _lock:
        return _paused


def set_paused(state: bool):
    global _paused
    with _lock:
        _paused = state
    logger.info("Agents %s", "PAUSED" if state else "RESUMED")


def toggle() -> bool:
    global _paused
    with _lock:
        _paused = not _paused
    logger.info("Agents %s", "PAUSED" if _paused else "RESUMED")
    return _paused
