import os
import time
import logging
from decimal import Decimal
from typing import Optional

import anthropic

logger = logging.getLogger(__name__)

MODEL_PRICING = {
    "claude-sonnet-4-6":         {"input": 3.0, "output": 15.0, "cache_read": 0.30, "cache_write": 3.75},
    "claude-haiku-4-5-20251001": {"input": 1.0, "output": 5.0,  "cache_read": 0.10, "cache_write": 1.25},
}


def get_supabase():
    from orchestrator.db import get_supabase as _get
    return _get()


class BaseAgent:
    name: str = "base"
    display_name: str = "Base Agent"
    model: str = "claude-sonnet-4-6"
    system_prompt: str = "You are a helpful assistant."
    slack_channel: str = "#ai-marketing-team"
    emoji: str = "🤖"

    MAX_RETRIES = 3
    BACKOFF_BASE = 2

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY must be set. "
                "On Railway, add it in Settings → Variables."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db = get_supabase()

    # ── core API call with cost logging + retry ──

    def call(
        self,
        user_message: str,
        history: Optional[list] = None,
        task_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        use_thinking: bool = False,
    ) -> dict:
        messages = list(history or [])
        messages.append({"role": "user", "content": user_message})

        system_block = [
            {
                "type": "text",
                "text": self.system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

        kwargs = dict(
            model=self.model,
            max_tokens=4096,
            system=system_block,
            messages=messages,
        )

        if use_thinking and "sonnet" in self.model:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": 2048}

        response = self._call_with_retry(**kwargs)
        cost_info = self._log_cost(response, task_id, campaign_id)
        text = self._extract_text(response)

        self._log_activity("response", text[:300], task_id)

        return {
            "text": text,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "cost": cost_info,
            "model": response.model,
        }

    def _call_with_retry(self, **kwargs):
        for attempt in range(self.MAX_RETRIES):
            try:
                return self.client.messages.create(**kwargs)
            except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError) as e:
                if attempt == self.MAX_RETRIES - 1:
                    self._log_activity("error", f"API call failed after {self.MAX_RETRIES} retries: {e}")
                    raise
                wait = self.BACKOFF_BASE ** (attempt + 1)
                logger.warning("Retry %d/%d for %s in %ds: %s", attempt + 1, self.MAX_RETRIES, self.name, wait, e)
                time.sleep(wait)

    @staticmethod
    def _extract_text(response) -> str:
        parts = []
        for block in response.content:
            if block.type == "text":
                parts.append(block.text)
        return "\n".join(parts)

    # ── cost logging ──

    def _log_cost(self, response, task_id=None, campaign_id=None) -> dict:
        pricing = MODEL_PRICING.get(self.model, MODEL_PRICING["claude-sonnet-4-6"])
        usage = response.usage

        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
        cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0

        cost = (
            (input_tokens / 1_000_000) * pricing["input"]
            + (output_tokens / 1_000_000) * pricing["output"]
            + (cache_read / 1_000_000) * pricing["cache_read"]
            + (cache_write / 1_000_000) * pricing["cache_write"]
        )

        row = {
            "agent_name": self.name,
            "model": response.model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": cache_read,
            "cache_write_tokens": cache_write,
            "estimated_cost_usd": float(Decimal(str(cost)).quantize(Decimal("0.000001"))),
        }
        if task_id:
            row["task_id"] = task_id
        if campaign_id:
            row["campaign_id"] = campaign_id

        try:
            self.db.table("agent_costs").insert(row).execute()
        except Exception as e:
            logger.error("Failed to log cost for %s: %s", self.name, e)

        return row

    # ── activity logging ──

    def _log_activity(self, action: str, details: str = "", task_id: str = None):
        row = {
            "agent_name": self.name,
            "action": action,
            "details": details[:500],
            "channel": self.slack_channel,
        }
        if task_id:
            row["task_id"] = task_id
        try:
            self.db.table("agent_activity").insert(row).execute()
        except Exception as e:
            logger.error("Failed to log activity for %s: %s", self.name, e)

    # ── knowledge base helpers ──

    def query_knowledge(self, topic: str, niche: str = None, limit: int = 5) -> list:
        try:
            q = (
                self.db.table("agent_knowledge")
                .select("category, topic, niche, approved_output, feedback_history, tags")
                .eq("agent_name", self.name)
                .ilike("topic", f"%{topic}%")
                .order("created_at", desc=True)
                .limit(limit)
            )
            if niche:
                q = q.ilike("niche", f"%{niche}%")
            result = q.execute()
            return result.data or []
        except Exception as e:
            logger.error("Knowledge query failed for %s: %s", self.name, e)
            return []

    def call_with_knowledge(
        self,
        user_message: str,
        topic: str,
        niche: str = None,
        history: Optional[list] = None,
        task_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        use_thinking: bool = False,
    ) -> dict:
        knowledge = self.query_knowledge(topic, niche)
        augmented = user_message
        if knowledge:
            refs = "\n---\n".join(
                f"[{k['category']}] {k['topic']}: {k['approved_output'][:600]}"
                for k in knowledge
            )
            augmented = (
                f"{user_message}\n\n"
                f"<reference>\nPreviously approved work on similar topics:\n{refs}\n</reference>"
            )

        return self.call(augmented, history, task_id, campaign_id, use_thinking)
