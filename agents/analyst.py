from agents.base_agent import BaseAgent


class SubodhAnalyst(BaseAgent):
    name = "subodh"
    display_name = "Subodh -- Analyst"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"

    system_prompt = (
        "You are Subodh, data analyst. Numbers-first, concise.\n\n"
        "OUTPUT FORMAT (under 300 words):\n"
        "Summary: [2 sentences max]\n"
        "Key findings: [3-5 bullet points with numbers]\n"
        "Recommendations: [3 prioritized action items]\n\n"
        "RULES:\n"
        "- Lead with the most impactful finding\n"
        "- Percentages and comparisons, not raw numbers alone\n"
        "- Say 'insufficient data' if needed -- never fabricate\n"
        "- No filler paragraphs. Bullets only."
    )

    def analyze_trends(
        self, research_data: str, niche: str = "",
        task_id: str = None, campaign_id: str = None,
    ) -> dict:
        return self.call_with_knowledge(
            user_message=(
                f"Analyze and give findings. Bullets only, no essays:\n\n"
                f"<data>\n{research_data}\n</data>"
            ),
            topic=niche or "trend analysis", niche=niche,
            task_id=task_id, campaign_id=campaign_id, use_thinking=True,
        )

    def campaign_report(
        self, campaign_data: str,
        task_id: str = None, campaign_id: str = None,
    ) -> dict:
        return self.call(
            user_message=f"Campaign report. Summary + bullets + recommendations:\n\n{campaign_data}",
            task_id=task_id, campaign_id=campaign_id,
        )
