from agents.base_agent import BaseAgent


class AnanyaCopywriter(BaseAgent):
    name = "ananya"
    display_name = "Ananya -- Copywriter"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"

    system_prompt = (
        "You are Ananya, copywriter. Write what's asked -- nothing extra.\n\n"
        "FORMATS:\n"
        "Blog: headline + meta desc (155 chars) + H2 outline + body + CTA. 800-1500 words max.\n"
        "Email: subject + preview + body + CTA. Under 300 words.\n"
        "Ad: headline + body + CTA + char counts. Under 100 words.\n\n"
        "RULES:\n"
        "- Use SEO keywords from Priya naturally\n"
        "- No filler, no fluff, no throat-clearing intros\n"
        "- Every paragraph must earn its place\n"
        "- Start with the deliverable, not commentary about it"
    )

    def write_content(
        self, task_description: str, research_context: str = "",
        topic: str = "", niche: str = "",
        task_id: str = None, campaign_id: str = None,
    ) -> dict:
        message = f"Write this. Start with the content directly, no preamble:\n\n{task_description}"
        if research_context:
            message += f"\n\n<research_brief>\n{research_context}\n</research_brief>"
        return self.call_with_knowledge(
            user_message=message, topic=topic or task_description[:100],
            niche=niche, task_id=task_id, campaign_id=campaign_id, use_thinking=True,
        )

    def revise_content(
        self, original: str, feedback: str,
        task_id: str = None, campaign_id: str = None,
    ) -> dict:
        return self.call(
            user_message=(
                f"Revise based on feedback. Return only the revised content:\n\n"
                f"<original>\n{original}\n</original>\n\n"
                f"<feedback>\n{feedback}\n</feedback>"
            ),
            task_id=task_id, campaign_id=campaign_id,
        )
