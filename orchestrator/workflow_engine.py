"""
Workflow templates — DAGs defining task dependency graphs for different campaign types.
Each workflow is research-first: research phases must complete before content creation.
"""


def blog_campaign_tasks(campaign_id: str, brief: str) -> list[dict]:
    """Blog campaign: research -> keywords -> write -> social -> wrapup."""
    return [
        {
            "campaign_id": campaign_id,
            "title": "Keyword & Newsletter Research",
            "description": f"Research keywords, newsletters, and ad library trends for: {brief}",
            "assigned_agent": "priya",
            "status": "backlog",
            "priority": 5,
            "depends_on": [],
            "_step": "research",
        },
        {
            "campaign_id": campaign_id,
            "title": "Trend & Competitor Analysis",
            "description": f"Analyze market trends and competitor content for: {brief}",
            "assigned_agent": "subodh",
            "status": "backlog",
            "priority": 5,
            "depends_on": [],
            "_step": "research",
        },
        {
            "campaign_id": campaign_id,
            "title": "Write Blog Post",
            "description": f"Write blog post based on approved research brief for: {brief}",
            "assigned_agent": "ananya",
            "status": "backlog",
            "priority": 4,
            "depends_on": ["Keyword & Newsletter Research", "Trend & Competitor Analysis"],
            "_step": "content",
        },
        {
            "campaign_id": campaign_id,
            "title": "Social Media Distribution Plan",
            "description": "Create social posts and content calendar from approved blog",
            "assigned_agent": "ramesh",
            "status": "backlog",
            "priority": 3,
            "depends_on": ["Write Blog Post"],
            "_step": "distribution",
        },
        {
            "campaign_id": campaign_id,
            "title": "Campaign Wrap-up & Cost Summary",
            "description": "Update Kanban, post summary with cost breakdown",
            "assigned_agent": "kavya",
            "status": "backlog",
            "priority": 1,
            "depends_on": ["Social Media Distribution Plan"],
            "_step": "wrapup",
        },
    ]


def newsletter_campaign_tasks(campaign_id: str, brief: str) -> list[dict]:
    """Newsletter campaign: research -> write newsletter -> social teasers -> wrapup."""
    return [
        {
            "campaign_id": campaign_id,
            "title": "Newsletter Niche Research",
            "description": f"Scan newsletters, ad library, and keyword trends for: {brief}",
            "assigned_agent": "priya",
            "status": "backlog",
            "priority": 5,
            "depends_on": [],
            "_step": "research",
        },
        {
            "campaign_id": campaign_id,
            "title": "Market Trend Analysis",
            "description": f"Competitor and trend analysis for newsletter topic: {brief}",
            "assigned_agent": "subodh",
            "status": "backlog",
            "priority": 5,
            "depends_on": [],
            "_step": "research",
        },
        {
            "campaign_id": campaign_id,
            "title": "Write Newsletter",
            "description": f"Write newsletter based on approved research for: {brief}",
            "assigned_agent": "ananya",
            "status": "backlog",
            "priority": 4,
            "depends_on": ["Newsletter Niche Research", "Market Trend Analysis"],
            "_step": "content",
        },
        {
            "campaign_id": campaign_id,
            "title": "Social Teasers for Newsletter",
            "description": "Create social media teasers to promote the newsletter",
            "assigned_agent": "ramesh",
            "status": "backlog",
            "priority": 3,
            "depends_on": ["Write Newsletter"],
            "_step": "distribution",
        },
        {
            "campaign_id": campaign_id,
            "title": "Campaign Wrap-up",
            "description": "Finalize Kanban, post cost summary",
            "assigned_agent": "kavya",
            "status": "backlog",
            "priority": 1,
            "depends_on": ["Social Teasers for Newsletter"],
            "_step": "wrapup",
        },
    ]


def email_campaign_tasks(campaign_id: str, brief: str) -> list[dict]:
    """Email sequence campaign: research -> write sequence -> social teasers -> wrapup."""
    return [
        {
            "campaign_id": campaign_id,
            "title": "Email Topic & Keyword Research",
            "description": f"Research keywords and newsletter trends for email campaign: {brief}",
            "assigned_agent": "priya",
            "status": "backlog",
            "priority": 5,
            "depends_on": [],
            "_step": "research",
        },
        {
            "campaign_id": campaign_id,
            "title": "Write Email Sequence",
            "description": f"Write email sequence based on approved research: {brief}",
            "assigned_agent": "ananya",
            "status": "backlog",
            "priority": 4,
            "depends_on": ["Email Topic & Keyword Research"],
            "_step": "content",
        },
        {
            "campaign_id": campaign_id,
            "title": "Social Teasers for Email Campaign",
            "description": "Create social posts to drive email signups",
            "assigned_agent": "ramesh",
            "status": "backlog",
            "priority": 3,
            "depends_on": ["Write Email Sequence"],
            "_step": "distribution",
        },
        {
            "campaign_id": campaign_id,
            "title": "Campaign Wrap-up",
            "description": "Finalize tracking and cost summary",
            "assigned_agent": "kavya",
            "status": "backlog",
            "priority": 1,
            "depends_on": ["Social Teasers for Email Campaign"],
            "_step": "wrapup",
        },
    ]


WORKFLOW_TEMPLATES = {
    "blog": blog_campaign_tasks,
    "newsletter": newsletter_campaign_tasks,
    "email": email_campaign_tasks,
}


def detect_workflow_type(brief: str) -> str:
    brief_lower = brief.lower()
    if any(w in brief_lower for w in ["newsletter", "digest", "weekly update"]):
        return "newsletter"
    if any(w in brief_lower for w in ["email", "drip", "sequence", "nurture"]):
        return "email"
    return "blog"
