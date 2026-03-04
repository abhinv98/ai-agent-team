from agents.base_agent import BaseAgent


class RameshSocial(BaseAgent):
    name = "ramesh"
    display_name = "Ramesh -- Social"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"

    system_prompt = (
        "You are Ramesh, social media manager. Platform-savvy, concise.\n\n"
        "OUTPUT: Table format only. No essays.\n\n"
        "CALENDAR FORMAT:\n"
        "Day | Platform | Type | Caption | Hashtags | CTA\n"
        "5-7 posts/week. Ready to publish -- not descriptions of posts.\n\n"
        "PLATFORM LIMITS:\n"
        "LinkedIn: 150-250 words, max 5 hashtags\n"
        "X: under 280 chars, 2-3 hashtags\n"
        "Instagram: storytelling caption, hashtags in comment\n\n"
        "RULES: Write actual post copy, not summaries of what you'd write. "
        "Wait for approved content before creating promotion posts."
    )

    def create_social_plan(
        self, content: str, topic: str = "", niche: str = "",
        ad_trends: str = "", task_id: str = None, campaign_id: str = None,
    ) -> dict:
        message = f"Social plan for this content. Table format, actual post copy:\n\n{content}"
        if ad_trends:
            message += f"\n\n<ad_trends>\n{ad_trends}\n</ad_trends>"
        return self.call_with_knowledge(
            user_message=message, topic=topic or content[:100], niche=niche,
            task_id=task_id, campaign_id=campaign_id, use_thinking=True,
        )

    def create_content_calendar(
        self, theme: str, weeks: int = 1,
        task_id: str = None, campaign_id: str = None,
    ) -> dict:
        return self.call(
            user_message=f"{weeks}-week content calendar for: {theme}. Table format, actual copy.",
            task_id=task_id, campaign_id=campaign_id,
        )
