from fastapi import APIRouter, Query
from datetime import datetime, timezone

from dashboard.api.database import get_db
from orchestrator.cost_tracker import get_daily_cost, get_daily_breakdown, get_hourly_breakdown, get_campaign_cost

router = APIRouter(prefix="/api/costs", tags=["costs"])


@router.get("/daily")
def daily_costs(days: int = Query(7, ge=1, le=90)):
    return get_daily_breakdown(days)


@router.get("/hourly")
def hourly_costs(hours: int = Query(24, ge=1, le=168)):
    return get_hourly_breakdown(hours)


@router.get("/summary")
def cost_summary():
    db = get_db()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    all_costs = db.table("agent_costs").select(
        "agent_name, estimated_cost_usd, created_at"
    ).execute().data or []

    agents: dict[str, dict] = {}
    for c in all_costs:
        name = c["agent_name"]
        if name not in agents:
            agents[name] = {"agent_name": name, "total_cost": 0.0, "today_cost": 0.0, "total_calls": 0, "today_calls": 0}
        cost = float(c["estimated_cost_usd"])
        agents[name]["total_cost"] += cost
        agents[name]["total_calls"] += 1
        if c["created_at"][:10] == today:
            agents[name]["today_cost"] += cost
            agents[name]["today_calls"] += 1

    return list(agents.values())


@router.get("/campaign/{campaign_id}")
def campaign_costs(campaign_id: str):
    return get_campaign_cost(campaign_id)
