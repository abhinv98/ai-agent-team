from agents.base_agent import BaseAgent


class PriyaSEO(BaseAgent):
    name = "priya"
    display_name = "Priya -- SEO"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"

    system_prompt = (
        "You are Priya, SEO specialist. Data-first, concise.\n\n"
        "KEYWORD BRIEF FORMAT (under 300 words):\n"
        "Primary: [keyword] ([volume estimate])\n"
        "Secondary: [5-8 keywords]\n"
        "Long-tail: [5-8 phrases]\n"
        "Intent: [informational/transactional/navigational]\n"
        "Angle: [1-2 sentences on how to rank]\n"
        "Gaps: [what competitors miss]\n\n"
        "RESEARCH BRIEF FORMAT (under 400 words):\n"
        "Newsletter trends: [bullet points]\n"
        "Ad library signals: [bullet points]\n"
        "Recommendation: [2-3 sentences]\n\n"
        "RULES: No essays. Bullet points and tables only. Cite sources. "
        "Deliver briefs BEFORE content creation."
    )

    def keyword_research(
        self, topic: str, research_data: str = "",
        niche: str = "", task_id: str = None, campaign_id: str = None,
    ) -> dict:
        message = f"Keyword brief for: {topic}. Bullets and data only, no prose."
        if research_data:
            message += f"\n\n<research_data>\n{research_data}\n</research_data>"
        return self.call_with_knowledge(
            user_message=message, topic=topic, niche=niche,
            task_id=task_id, campaign_id=campaign_id, use_thinking=True,
        )

    def create_research_brief(
        self, topic: str, newsletter_data: dict, ad_data: dict,
        niche: str = "", task_id: str = None, campaign_id: str = None,
    ) -> dict:
        message = (
            f"Research brief for: {topic}. Keep it tight.\n\n"
            f"<newsletters>\n{_summarize(newsletter_data)}\n</newsletters>\n\n"
            f"<ad_library>\n{_summarize(ad_data)}\n</ad_library>"
        )
        return self.call_with_knowledge(
            user_message=message, topic=topic, niche=niche,
            task_id=task_id, campaign_id=campaign_id, use_thinking=True,
        )


def _summarize(data: dict) -> str:
    if not data:
        return "No data available."
    if "summary" in data:
        return data["summary"]
    return str(data)[:2000]
