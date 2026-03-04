from fastapi import APIRouter, Query
from pydantic import BaseModel

from dashboard.api.database import get_db
from slack_app.channel_config import AGENT_DISPLAY
from orchestrator.killswitch import is_paused, set_paused

router = APIRouter(prefix="/api/agents", tags=["agents"])


class PauseRequest(BaseModel):
    paused: bool


@router.get("/status")
def agent_status():
    db = get_db()
    statuses = []

    for name, display in AGENT_DISPLAY.items():
        active_tasks = (
            db.table("tasks")
            .select("id, title")
            .eq("assigned_agent", name)
            .eq("status", "in_progress")
            .execute()
            .data or []
        )

        pending = (
            db.table("tasks")
            .select("id")
            .eq("assigned_agent", name)
            .eq("status", "pending_review")
            .execute()
            .data or []
        )

        if active_tasks:
            status = "working"
            current_task = active_tasks[0]["title"]
        elif pending:
            status = "waiting"
            current_task = None
        else:
            status = "idle"
            current_task = None

        statuses.append({
            "name": name,
            "display_name": display["name"],
            "color": display["color"],
            "status": status,
            "current_task": current_task,
        })

    return statuses


@router.get("/paused")
def get_paused():
    return {"paused": is_paused()}


@router.post("/paused")
def set_paused_state(req: PauseRequest):
    set_paused(req.paused)
    return {"paused": is_paused()}


@router.get("/activity")
def agent_activity(limit: int = Query(50, ge=1, le=200)):
    db = get_db()
    return (
        db.table("agent_activity")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data or []
    )
