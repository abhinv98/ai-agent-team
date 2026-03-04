"""
Task router — resolves DAG dependencies and triggers agents when tasks are unblocked.
"""
import asyncio
import logging
from typing import Optional

from orchestrator.db import get_supabase
from orchestrator import research_engine
from orchestrator.knowledge_base import store_research_finding

logger = logging.getLogger(__name__)

_agent_instances = {}


def get_agent(name: str):
    if name not in _agent_instances:
        _init_agents()
    return _agent_instances.get(name)


def _init_agents():
    if _agent_instances:
        return
    from agents import (
        MayaStrategist, AnanyaCopywriter, PriyaSEO,
        RameshSocial, SubodhAnalyst, KavyaPM,
    )
    _agent_instances.update({
        "maya": MayaStrategist(),
        "ananya": AnanyaCopywriter(),
        "priya": PriyaSEO(),
        "ramesh": RameshSocial(),
        "subodh": SubodhAnalyst(),
        "kavya": KavyaPM(),
    })


def get_tasks_for_campaign(campaign_id: str) -> list[dict]:
    db = get_supabase()
    result = db.table("tasks").select("*").eq("campaign_id", campaign_id).execute()
    return result.data or []


def get_task(task_id: str) -> Optional[dict]:
    db = get_supabase()
    result = db.table("tasks").select("*").eq("id", task_id).execute()
    return result.data[0] if result.data else None


def update_task(task_id: str, updates: dict):
    db = get_supabase()
    db.table("tasks").update(updates).eq("id", task_id).execute()


def create_tasks_for_campaign(campaign_id: str, task_defs: list[dict]) -> list[dict]:
    """Insert task definitions into DB, resolving title-based depends_on to UUIDs."""
    db = get_supabase()
    created = []
    title_to_id = {}

    for tdef in task_defs:
        row = {
            "campaign_id": tdef["campaign_id"],
            "title": tdef["title"],
            "description": tdef.get("description", ""),
            "assigned_agent": tdef["assigned_agent"],
            "status": tdef.get("status", "backlog"),
            "priority": tdef.get("priority", 0),
            "depends_on": [],
        }
        result = db.table("tasks").insert(row).execute()
        task = result.data[0]
        created.append(task)
        title_to_id[tdef["title"]] = task["id"]

    for i, tdef in enumerate(task_defs):
        dep_titles = tdef.get("depends_on", [])
        if dep_titles:
            dep_ids = [title_to_id[t] for t in dep_titles if t in title_to_id]
            if dep_ids:
                db.table("tasks").update({"depends_on": dep_ids}).eq("id", created[i]["id"]).execute()
                created[i]["depends_on"] = dep_ids

    return created


def get_unblocked_tasks(campaign_id: str) -> list[dict]:
    """Find tasks in backlog whose dependencies are all approved/done."""
    tasks = get_tasks_for_campaign(campaign_id)
    completed_ids = {t["id"] for t in tasks if t["status"] in ("approved", "done")}

    unblocked = []
    for t in tasks:
        if t["status"] != "backlog":
            continue
        deps = t.get("depends_on") or []
        if all(d in completed_ids for d in deps):
            unblocked.append(t)
    return unblocked


async def trigger_agent_for_task(task: dict, upstream_outputs: Optional[dict] = None) -> dict:
    """Execute the assigned agent for a task, passing upstream context."""
    agent_name = task["assigned_agent"]
    agent = get_agent(agent_name)
    if not agent:
        logger.error("No agent found for: %s", agent_name)
        return {"error": f"Unknown agent: {agent_name}"}

    update_task(task["id"], {"status": "in_progress"})

    context_parts = [task.get("description", "")]
    if upstream_outputs:
        for upstream_agent, output in upstream_outputs.items():
            context_parts.append(f"\n<{upstream_agent}_output>\n{output}\n</{upstream_agent}_output>")
    full_context = "\n".join(context_parts)

    campaign = None
    if task.get("campaign_id"):
        db = get_supabase()
        r = db.table("campaigns").select("brief").eq("id", task["campaign_id"]).execute()
        if r.data:
            campaign = r.data[0]

    niche = campaign.get("brief", "")[:100] if campaign else ""

    if agent_name == "priya":
        research_data = await research_engine.run_full_research(niche, task_id=task["id"])
        research_summary = research_data.get("summary", "")
        result = agent.keyword_research(
            topic=task["title"], research_data=f"{full_context}\n\n{research_summary}",
            niche=niche, task_id=task["id"], campaign_id=task.get("campaign_id"),
        )
    elif agent_name == "subodh":
        research_data = await research_engine.analyze_competitor_content(niche, task_id=task["id"])
        result = agent.analyze_trends(
            research_data=f"{full_context}\n\n{research_data.get('summary', '')}",
            niche=niche, task_id=task["id"], campaign_id=task.get("campaign_id"),
        )
    elif agent_name == "ananya":
        result = agent.write_content(
            task_description=full_context, niche=niche,
            topic=task["title"], task_id=task["id"], campaign_id=task.get("campaign_id"),
        )
    elif agent_name == "ramesh":
        result = agent.create_social_plan(
            content=full_context, niche=niche,
            topic=task["title"], task_id=task["id"], campaign_id=task.get("campaign_id"),
        )
    elif agent_name == "kavya":
        tasks_summary = _build_tasks_summary(task.get("campaign_id"))
        result = agent.generate_standup(tasks_summary)
    else:
        result = agent.call(
            user_message=full_context,
            task_id=task["id"], campaign_id=task.get("campaign_id"),
        )

    update_task(task["id"], {
        "status": "pending_review",
        "output_content": result.get("text", "")[:10000],
    })

    return result


async def process_approved_task(task_id: str):
    """When a task is approved, find and trigger downstream tasks."""
    task = get_task(task_id)
    if not task:
        return

    campaign_id = task.get("campaign_id")
    if not campaign_id:
        return

    unblocked = get_unblocked_tasks(campaign_id)

    approved_tasks = get_tasks_for_campaign(campaign_id)
    upstream_outputs = {}
    for t in approved_tasks:
        if t["status"] in ("approved", "done") and t.get("output_content"):
            upstream_outputs[t["assigned_agent"]] = t["output_content"]

    for unblocked_task in unblocked:
        await trigger_agent_for_task(unblocked_task, upstream_outputs)


def _build_tasks_summary(campaign_id: Optional[str] = None) -> dict:
    db = get_supabase()
    q = db.table("tasks").select("status")
    if campaign_id:
        q = q.eq("campaign_id", campaign_id)
    tasks = q.execute().data or []

    summary = {}
    for t in tasks:
        s = t["status"]
        summary[s] = summary.get(s, 0) + 1
    return summary
