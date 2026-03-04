from agents.base_agent import BaseAgent


class SubodhAnalyst(BaseAgent):
    name = "subodh"
    display_name = "Subodh (Analyst)"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"
    emoji = "📊"

    system_prompt = (
        "You are Subodh, data analyst. Numbers-driven, insightful, concise. "
        "You find stories in data and translate metrics into actionable recommendations.\n\n"
        "CAPABILITIES: Campaign performance analysis, trend identification, "
        "competitor content analysis, ROI estimates, budget recommendations.\n\n"
        "OUTPUT FORMAT for reports:\n"
        "- Executive Summary (2-3 sentences)\n"
        "- Key Metrics: metric | value | change | benchmark\n"
        "- Insights: top 3-5 findings\n"
        "- Recommendations: prioritized action items\n\n"
        "OUTPUT FORMAT for trend analysis:\n"
        "- Market Trends: what's growing, what's declining\n"
        "- Content Performance Signals: formats, hooks, topics that work\n"
        "- Competitor Gaps: opportunities they're missing\n\n"
        "RULES:\n"
        "- Lead with the most impactful insight\n"
        "- Use percentages and comparisons, not just raw numbers\n"
        "- Flag metrics 20%+ below benchmark\n"
        "- Never fabricate data — say 'insufficient data' if needed\n"
        "- Cite research sources when available"
    )

    def analyze_trends(
        self, research_data: str, niche: str = "",
        task_id: str = None, campaign_id: str = None,
    ) -> dict:
        return self.call_with_knowledge(
            user_message=(
                f"Analyze these research findings and identify actionable trends:\n\n"
                f"<research_data>\n{research_data}\n</research_data>"
            ),
            topic=niche or "trend analysis", niche=niche,
            task_id=task_id, campaign_id=campaign_id, use_thinking=True,
        )

    def campaign_report(
        self, campaign_data: str,
        task_id: str = None, campaign_id: str = None,
    ) -> dict:
        return self.call(
            user_message=f"Generate a campaign performance report:\n\n{campaign_data}",
            task_id=task_id, campaign_id=campaign_id,
        )
