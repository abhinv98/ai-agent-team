from agents.base_agent import BaseAgent


class AnanyaCopywriter(BaseAgent):
    name = "ananya"
    display_name = "Ananya (Copywriter)"
    model = "claude-sonnet-4-6"
    slack_channel = "#ai-marketing-team"
    emoji = "✍️"

    system_prompt = (
        "You are Ananya, senior copywriter. Creative, versatile — you switch between "
        "formal B2B and casual B2C effortlessly. Passionate about compelling narratives and clear CTAs.\n\n"
        "CAPABILITIES: Blog posts (800-2000 words), email sequences, ad copy, landing pages, newsletters.\n\n"
        "OUTPUT FORMAT:\n"
        "- Blog: headline, meta description (155 chars), H2/H3 structure, CTA\n"
        "- Email: subject line, preview text, body, CTA\n"
        "- Ad: headline, body, CTA, character counts\n"
        "- Newsletter: subject, sections with headers, CTA per section\n\n"
        "RULES:\n"
        "- Always incorporate SEO keywords from Priya naturally — never keyword-stuff\n"
        "- Wait for research brief before writing SEO content\n"
        "- 'Make it punchier' = shorter sentences, power verbs, remove filler\n"
        "- 'More professional' = no contractions, add data points, formal tone\n"
        "- Reference approved past work when available for consistency"
    )

    def write_content(
        self, task_description: str, research_context: str = "",
        topic: str = "", niche: str = "",
        task_id: str = None, campaign_id: str = None,
    ) -> dict:
        message = task_description
        if research_context:
            message = f"{task_description}\n\n<research_brief>\n{research_context}\n</research_brief>"
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
                f"Revise this content based on feedback.\n\n"
                f"<original>\n{original}\n</original>\n\n"
                f"<feedback>\n{feedback}\n</feedback>"
            ),
            task_id=task_id, campaign_id=campaign_id,
        )
