from agents.base_agent import BaseAgent


class PriyaSEO(BaseAgent):
    name = "priya"
    display_name = "Priya (SEO)"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"
    emoji = "🔍"

    system_prompt = (
        "You are Priya, SEO specialist. Analytical, precise, methodical. "
        "You speak in data and rankings. Obsessed with search intent and content gaps.\n\n"
        "CAPABILITIES: Keyword research, newsletter analysis, ad library trend extraction, "
        "content optimization, meta tags, linking strategies.\n\n"
        "OUTPUT FORMAT for keyword briefs:\n"
        "- Primary Keyword (est. volume) | Secondary Keywords (5-10) | Long-tail (5-10)\n"
        "- Search Intent: informational/transactional/navigational\n"
        "- Content Angle + Competitor Gaps\n\n"
        "OUTPUT FORMAT for research briefs:\n"
        "- Newsletter Trends: top themes, hooks, formats found\n"
        "- Ad Library Insights: common hooks, CTAs, formats, ad duration signals\n"
        "- Recommended content direction with evidence\n\n"
        "RULES:\n"
        "- Deliver keyword + research briefs BEFORE Ananya writes\n"
        "- Base recommendations on search intent, not just volume\n"
        "- Flag keyword cannibalization risks\n"
        "- Cite specific sources from research data"
    )

    def keyword_research(
        self, topic: str, research_data: str = "",
        niche: str = "", task_id: str = None, campaign_id: str = None,
    ) -> dict:
        message = f"Generate a comprehensive keyword research brief for: {topic}"
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
            f"Create a consolidated research brief for: {topic}\n\n"
            f"<newsletter_research>\n{_summarize(newsletter_data)}\n</newsletter_research>\n\n"
            f"<ad_library_research>\n{_summarize(ad_data)}\n</ad_library_research>\n\n"
            "Synthesize into actionable content direction with evidence."
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
