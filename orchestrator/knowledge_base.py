import logging
from typing import Optional

from orchestrator.db import get_supabase

logger = logging.getLogger(__name__)


def store_approved_output(
    agent_name: str,
    category: str,
    topic: str,
    approved_output: str,
    task_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    niche: Optional[str] = None,
    input_context: Optional[str] = None,
    feedback_history: Optional[list] = None,
    tags: Optional[list[str]] = None,
    approved_by: Optional[str] = None,
) -> dict:
    db = get_supabase()
    row = {
        "agent_name": agent_name,
        "category": category,
        "topic": topic,
        "approved_output": approved_output,
        "feedback_history": feedback_history or [],
        "tags": tags or [],
    }
    if task_id:
        row["task_id"] = task_id
    if campaign_id:
        row["campaign_id"] = campaign_id
    if niche:
        row["niche"] = niche
    if input_context:
        row["input_context"] = input_context
    if approved_by:
        row["approved_by"] = approved_by

    try:
        result = db.table("agent_knowledge").insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as e:
        logger.error("Failed to store approved output: %s", e)
        return row


def query_knowledge(
    agent_name: str,
    topic: str,
    niche: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 5,
) -> list[dict]:
    db = get_supabase()
    try:
        q = (
            db.table("agent_knowledge")
            .select("*")
            .eq("agent_name", agent_name)
            .ilike("topic", f"%{topic}%")
            .order("created_at", desc=True)
            .limit(limit)
        )
        if niche:
            q = q.ilike("niche", f"%{niche}%")
        if category:
            q = q.eq("category", category)
        return q.execute().data or []
    except Exception as e:
        logger.error("Knowledge query failed: %s", e)
        return []


def store_research_finding(
    agent_name: str,
    research_type: str,
    niche: str,
    summary: str,
    task_id: Optional[str] = None,
    source: Optional[str] = None,
    raw_data: Optional[dict] = None,
    key_insights: Optional[list[str]] = None,
) -> dict:
    db = get_supabase()
    row = {
        "agent_name": agent_name,
        "research_type": research_type,
        "niche": niche,
        "summary": summary,
        "raw_data": raw_data or {},
        "key_insights": key_insights or [],
    }
    if task_id:
        row["task_id"] = task_id
    if source:
        row["source"] = source

    try:
        result = db.table("research_findings").insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as e:
        logger.error("Failed to store research finding: %s", e)
        return row


def get_research_for_niche(niche: str, research_type: Optional[str] = None, limit: int = 10) -> list[dict]:
    db = get_supabase()
    try:
        q = (
            db.table("research_findings")
            .select("*")
            .ilike("niche", f"%{niche}%")
            .order("created_at", desc=True)
            .limit(limit)
        )
        if research_type:
            q = q.eq("research_type", research_type)
        return q.execute().data or []
    except Exception as e:
        logger.error("Research query failed: %s", e)
        return []


def store_ad_library_snapshot(
    niche: str,
    query_term: str,
    ad_count: int = 0,
    top_ads: Optional[list] = None,
    trends: Optional[dict] = None,
) -> dict:
    db = get_supabase()
    row = {
        "niche": niche,
        "query_term": query_term,
        "ad_count": ad_count,
        "top_ads": top_ads or [],
        "trends": trends or {},
    }
    try:
        result = db.table("ad_library_snapshots").insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as e:
        logger.error("Failed to store ad library snapshot: %s", e)
        return row


def get_ad_library_trends(niche: str, limit: int = 5) -> list[dict]:
    db = get_supabase()
    try:
        return (
            db.table("ad_library_snapshots")
            .select("*")
            .ilike("niche", f"%{niche}%")
            .order("fetched_at", desc=True)
            .limit(limit)
            .execute()
            .data or []
        )
    except Exception as e:
        logger.error("Ad library query failed: %s", e)
        return []
