from fastapi import APIRouter

from dashboard.api.database import get_db
from dashboard.api.models import CampaignCreate

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.get("")
def list_campaigns():
    db = get_db()
    return db.table("campaigns").select("*").order("created_at", desc=True).execute().data or []


@router.post("")
def create_campaign(campaign: CampaignCreate):
    db = get_db()
    result = db.table("campaigns").insert({
        "name": campaign.name,
        "brief": campaign.brief,
        "status": "active",
    }).execute()
    return result.data[0] if result.data else {"error": "Creation failed"}


@router.get("/{campaign_id}")
def get_campaign(campaign_id: str):
    db = get_db()
    campaign = db.table("campaigns").select("*").eq("id", campaign_id).execute()
    tasks = db.table("tasks").select("*").eq("campaign_id", campaign_id).order("priority", desc=True).execute()

    costs = db.table("agent_costs").select("agent_name, estimated_cost_usd").eq("campaign_id", campaign_id).execute()
    total_cost = sum(float(c["estimated_cost_usd"]) for c in (costs.data or []))

    return {
        "campaign": campaign.data[0] if campaign.data else None,
        "tasks": tasks.data or [],
        "total_cost": total_cost,
    }
