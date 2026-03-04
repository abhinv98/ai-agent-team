from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_agent: Optional[str] = None
    priority: Optional[int] = None
    output_content: Optional[str] = None
    feedback: Optional[str] = None


class CampaignCreate(BaseModel):
    name: str
    brief: Optional[str] = None


class CostSummary(BaseModel):
    agent_name: str
    total_cost: float
    today_cost: float
    total_calls: int
    today_calls: int


class AgentStatus(BaseModel):
    name: str
    display_name: str
    emoji: str
    color: str
    status: str  # idle, working, waiting
    current_task: Optional[str] = None
