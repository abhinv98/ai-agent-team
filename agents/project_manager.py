from agents.base_agent import BaseAgent
from orchestrator.cost_tracker import get_daily_cost, check_budget_alert


class KavyaPM(BaseAgent):
    name = "kavya"
    display_name = "Kavya (PM)"
    model = "claude-haiku-4-5-20251001"
    slack_channel = "#ai-marketing-team"
    emoji = "📋"

    system_prompt = (
        "You are Kavya, project manager. Organized, proactive, clear communicator. "
        "You keep everyone on track without being pushy.\n\n"
        "CAPABILITIES: Task tracking, standup summaries, Kanban updates, "
        "cost alerts, campaign completion reports.\n\n"
        "OUTPUT FORMAT for standups:\n"
        "**Daily Standup — [Date]**\n"
        "Active Campaigns: [count]\n"
        "Tasks: Done [n] | In Progress [n] | Pending Review [n] | Backlog [n]\n"
        "Blockers: [list]\n"
        "Today's Cost: $[total] (breakdown by agent)\n\n"
        "RULES:\n"
        "- Alert if task in 'pending_review' > 24 hours\n"
        "- Alert if any agent's daily cost > $5\n"
        "- Always include cost data in summaries"
    )

    def generate_standup(self, tasks_summary: dict, campaign_count: int = 0) -> dict:
        cost_data = get_daily_cost()
        alerts = check_budget_alert()

        cost_str = "\n".join(
            f"- {c['agent_name']}: ${c['cost']:.4f} ({c['calls']} calls)"
            for c in cost_data
        ) if cost_data else "No API calls today."

        alert_str = ""
        if alerts:
            alert_str = "\n⚠️ BUDGET ALERTS: " + ", ".join(
                f"{a['agent_name']} at ${a['cost']:.2f}" for a in alerts
            )

        message = (
            f"Generate a standup summary with this data:\n\n"
            f"Active campaigns: {campaign_count}\n"
            f"Tasks: {tasks_summary}\n\n"
            f"Today's costs:\n{cost_str}{alert_str}"
        )
        return self.call(user_message=message)

    def campaign_wrapup(self, campaign_name: str, cost_data: dict, tasks_data: list) -> dict:
        return self.call(
            user_message=(
                f"Generate a campaign completion summary.\n"
                f"Campaign: {campaign_name}\n"
                f"Cost: {cost_data}\n"
                f"Tasks completed: {len(tasks_data)}"
            ),
        )
