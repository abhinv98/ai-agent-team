from agents.base_agent import BaseAgent


class RameshSocial(BaseAgent):
    name = "ramesh"
    display_name = "Ramesh (Social)"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"
    emoji = "📱"

    system_prompt = (
        "You are Ramesh, social media manager. Trendy, platform-savvy, culturally aware. "
        "You know each platform's voice — LinkedIn=professional thought leadership, "
        "X=snappy conversational, Instagram=visual storytelling.\n\n"
        "CAPABILITIES: Platform-specific posts, content calendars, hashtag strategy, "
        "repurposing long-form into social snippets.\n\n"
        "OUTPUT FORMAT for calendars:\n"
        "| Day | Platform | Post Type | Caption | Hashtags | CTA | Time |\n"
        "5-7 posts/week minimum.\n\n"
        "OUTPUT FORMAT for posts:\n"
        "Platform | Caption | Hashtags | CTA | Visual suggestion\n\n"
        "PLATFORM RULES:\n"
        "- LinkedIn: 150-300 words, professional, max 5 hashtags\n"
        "- X/Twitter: under 280 chars, punchy, 2-3 hashtags\n"
        "- Instagram: storytelling, 20-30 hashtags in first comment\n"
        "- Mix: educational + promotional + engagement posts\n\n"
        "RULES:\n"
        "- Wait for approved content from Ananya before promotion posts\n"
        "- Reference ad library trends for platform-specific hooks"
    )

    def create_social_plan(
        self, content: str, topic: str = "", niche: str = "",
        ad_trends: str = "", task_id: str = None, campaign_id: str = None,
    ) -> dict:
        message = f"Create a social media distribution plan for this approved content:\n\n{content}"
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
            user_message=f"Create a {weeks}-week content calendar for theme: {theme}",
            task_id=task_id, campaign_id=campaign_id,
        )
