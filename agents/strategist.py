from agents.base_agent import BaseAgent


class MayaStrategist(BaseAgent):
    name = "maya"
    display_name = "Maya -- CMO"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"

    system_prompt = (
        "You are Maya, CMO. You decompose campaign briefs into task plans.\n\n"
        "OUTPUT (keep it under 400 words total):\n"
        "Campaign: [name]\n"
        "Objective: [1 sentence]\n"
        "Audience: [1 sentence]\n"
        "Gaps: [flag anything missing from the brief]\n\n"
        "Tasks:\n"
        "# | Title | Agent | Dependencies | Priority\n"
        "[numbered rows]\n\n"
        "Order: research (Priya) -> content (Ananya) -> social (Ramesh) -> analysis (Subodh). "
        "Kavya=PM. Never start without human approval. Keep task descriptions to 1 line each."
    )

    def plan_campaign(self, brief: str, campaign_id: str = None) -> dict:
        return self.call_with_knowledge(
            user_message=f"Plan this campaign. Be concise -- table format, no essays:\n\n{brief}",
            topic=brief[:100],
            campaign_id=campaign_id,
            use_thinking=True,
        )
