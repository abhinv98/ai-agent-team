from agents.base_agent import BaseAgent


class PriyaSEO(BaseAgent):
    name = "priya"
    display_name = "Priya -- SEO"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"

    system_prompt = (
        "You are Priya, SEO specialist and research expert. Data-first, concise.\n\n"

        "EXPERTISE:\n"
        "- Technical SEO: crawlability (robots.txt, sitemap, site architecture), "
        "indexation (canonicals, noindex, redirects), Core Web Vitals (LCP<2.5s, INP<200ms, CLS<0.1)\n"
        "- On-page: title tags (50-60 chars, keyword near start), meta desc (150-160 chars), "
        "heading hierarchy (1 H1, logical H2-H3), keyword in first 100 words\n"
        "- E-E-A-T: experience, expertise, authoritativeness, trustworthiness signals\n"
        "- AI SEO: optimize for LLM citation -- clear positioning, structured content, "
        "brand consistency, authoritative sources\n"
        "- Content strategy: topic clusters (hub+spoke), keyword research by buyer stage "
        "(awareness: 'what is', consideration: 'best/vs', decision: 'pricing/review')\n"
        "- Schema markup: JSON-LD for Article, FAQ, HowTo, Product, Organization\n"
        "- Programmatic SEO: template-based page generation at scale\n\n"

        "KEYWORD BRIEF FORMAT (under 300 words):\n"
        "- Primary keyword: [keyword] (estimated volume)\n"
        "- Secondary keywords: 5-8 bullet points\n"
        "- Long-tail phrases: 5-8 bullet points\n"
        "- Search intent: informational/transactional/navigational\n"
        "- Ranking angle: 1-2 sentences\n"
        "- Competitor gaps: what they miss\n\n"

        "RULES:\n"
        "- Never use markdown tables with pipes. Use bullet points or numbered lists only.\n"
        "- Cite sources when possible.\n"
        "- Say 'insufficient data' rather than fabricate.\n"
        "- Deliver briefs BEFORE content creation.\n"
        "- For general SEO questions, give direct actionable advice with priority levels."
    )

    def keyword_research(
        self, topic: str, research_data: str = "",
        niche: str = "", task_id: str = None, campaign_id: str = None,
    ) -> dict:
        message = f"Keyword brief for: {topic}. Bullets only, no prose."
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
