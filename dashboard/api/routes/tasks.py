from fastapi import APIRouter, Query
from typing import Optional

from dashboard.api.database import get_db
from dashboard.api.models import TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
def list_tasks(
    status: Optional[str] = None,
    campaign_id: Optional[str] = None,
    agent: Optional[str] = None,
):
    db = get_db()
    q = db.table("tasks").select("*, campaigns(name)")
    if status:
        q = q.eq("status", status)
    if campaign_id:
        q = q.eq("campaign_id", campaign_id)
    if agent:
        q = q.eq("assigned_agent", agent)
    return q.order("priority", desc=True).order("created_at").execute().data or []


@router.get("/board")
def get_board(campaign_id: Optional[str] = None):
    db = get_db()
    q = db.table("tasks").select("*, campaigns(name)")
    if campaign_id:
        q = q.eq("campaign_id", campaign_id)
    tasks = q.order("priority", desc=True).order("created_at").execute().data or []

    columns = {
        "backlog": [], "in_progress": [], "pending_review": [],
        "changes_requested": [], "approved": [], "done": [],
    }
    for t in tasks:
        col = t.get("status", "backlog")
        if col in columns:
            columns[col].append(t)
    return columns


@router.get("/{task_id}")
def get_task(task_id: str):
    db = get_db()
    result = db.table("tasks").select("*, campaigns(name)").eq("id", task_id).execute()
    return result.data[0] if result.data else {"error": "Not found"}


@router.patch("/{task_id}")
def update_task(task_id: str, update: TaskUpdate):
    db = get_db()
    data = update.model_dump(exclude_none=True)
    if not data:
        return {"error": "No fields to update"}
    result = db.table("tasks").update(data).eq("id", task_id).execute()
    return result.data[0] if result.data else {"error": "Update failed"}
