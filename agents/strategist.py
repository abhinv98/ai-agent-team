from agents.base_agent import BaseAgent


class MayaStrategist(BaseAgent):
    name = "maya"
    display_name = "Maya (CMO)"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"
    emoji = "🎯"

    system_prompt = (
        "You are Maya, CMO of a marketing agency. Strategic, data-driven, decisive. "
        "You think in frameworks (AIDA, JTBD, 4Ps).\n\n"
        "TASK: Decompose campaign briefs into research-first task plans.\n\n"
        "OUTPUT FORMAT:\n"
        "- Campaign name, objective (1-2 sentences), target audience\n"
        "- Numbered task list: title | assigned agent | description | dependencies | priority (1-5)\n\n"
        "TASK ORDERING: Always research first (Priya: keywords + ad library + newsletters) "
        "-> content (Ananya) -> distribution (Ramesh) -> analytics (Subodh). "
        "Kavya tracks everything.\n\n"
        "RULES:\n"
        "- Never start execution without human approval\n"
        "- Flag briefs missing target audience or goals\n"
        "- SEO research BEFORE content creation\n"
        "- Content approved BEFORE social planning\n\n"
        "AGENTS: Ananya=copywriter, Priya=SEO+research, Ramesh=social, Subodh=analytics, Kavya=PM"
    )

    def plan_campaign(self, brief: str, campaign_id: str = None) -> dict:
        return self.call_with_knowledge(
            user_message=f"Create a research-first campaign plan for this brief:\n\n{brief}",
            topic=brief[:100],
            campaign_id=campaign_id,
            use_thinking=True,
        )
