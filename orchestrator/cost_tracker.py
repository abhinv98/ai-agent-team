import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from orchestrator.db import get_supabase

logger = logging.getLogger(__name__)


def get_daily_cost(agent_name: Optional[str] = None) -> list[dict]:
    db = get_supabase()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    q = (
        db.table("agent_costs")
        .select("agent_name, estimated_cost_usd, input_tokens, output_tokens")
        .gte("created_at", f"{today}T00:00:00Z")
    )
    if agent_name:
        q = q.eq("agent_name", agent_name)
    rows = q.execute().data or []

    totals: dict[str, dict] = {}
    for r in rows:
        name = r["agent_name"]
        if name not in totals:
            totals[name] = {"agent_name": name, "cost": 0.0, "calls": 0, "input_tokens": 0, "output_tokens": 0}
        totals[name]["cost"] += float(r["estimated_cost_usd"])
        totals[name]["calls"] += 1
        totals[name]["input_tokens"] += r["input_tokens"]
        totals[name]["output_tokens"] += r["output_tokens"]
    return list(totals.values())


def get_campaign_cost(campaign_id: str) -> dict:
    db = get_supabase()
    rows = (
        db.table("agent_costs")
        .select("agent_name, estimated_cost_usd, input_tokens, output_tokens")
        .eq("campaign_id", campaign_id)
        .execute()
        .data or []
    )
    total = 0.0
    by_agent: dict[str, float] = {}
    for r in rows:
        c = float(r["estimated_cost_usd"])
        total += c
        by_agent[r["agent_name"]] = by_agent.get(r["agent_name"], 0.0) + c
    return {"campaign_id": campaign_id, "total_cost": total, "by_agent": by_agent, "call_count": len(rows)}


def check_budget_alert(threshold: float = 5.0) -> list[dict]:
    daily = get_daily_cost()
    return [a for a in daily if a["cost"] >= threshold]


def get_daily_breakdown(days: int = 7) -> list[dict]:
    db = get_supabase()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
    rows = (
        db.table("agent_costs")
        .select("agent_name, estimated_cost_usd, created_at")
        .gte("created_at", since)
        .order("created_at")
        .execute()
        .data or []
    )

    breakdown: dict[str, dict[str, float]] = {}
    for r in rows:
        day = r["created_at"][:10]
        if day not in breakdown:
            breakdown[day] = {}
        name = r["agent_name"]
        breakdown[day][name] = breakdown[day].get(name, 0.0) + float(r["estimated_cost_usd"])

    return [{"date": d, **agents} for d, agents in sorted(breakdown.items())]


def get_hourly_breakdown(hours: int = 24) -> list[dict]:
    db = get_supabase()
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = (
        db.table("agent_costs")
        .select("agent_name, estimated_cost_usd, created_at")
        .gte("created_at", since)
        .order("created_at")
        .execute()
        .data or []
    )

    breakdown: dict[str, dict[str, float]] = {}
    for r in rows:
        hour = r["created_at"][:13]
        if hour not in breakdown:
            breakdown[hour] = {}
        name = r["agent_name"]
        breakdown[hour][name] = breakdown[hour].get(name, 0.0) + float(r["estimated_cost_usd"])

    return [{"hour": h, **agents} for h, agents in sorted(breakdown.items())]
