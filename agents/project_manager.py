from agents.base_agent import BaseAgent


class KavyaPM(BaseAgent):
    name = "kavya"
    display_name = "Kavya -- PM"
    model = "claude-haiku-4-5-20251001"
    slack_channel = "#ai-marketing-team"

    system_prompt = (
        "You are Kavya, project manager. Brief and clear.\n\n"
        "STANDUP FORMAT (under 150 words):\n"
        "- Campaigns: [count]\n"
        "- Done: [n] | In Progress: [n] | Review: [n] | Backlog: [n]\n"
        "- Blockers: [list or 'none']\n"
        "- Cost today: $[total] ([agent]: $[amount] each)\n"
        "- Alerts: [any budget warnings or 'none']\n\n"
        "RULES:\n"
        "- Never use markdown tables with pipes. Use bullet points only.\n"
        "- No commentary. Just the data."
    )

    def generate_standup(self, tasks_summary: dict, campaign_count: int = 0) -> dict:
        from orchestrator.cost_tracker import get_daily_cost, check_budget_alert
        cost_data = get_daily_cost()
        alerts = check_budget_alert()

        cost_str = ", ".join(
            f"{c['agent_name']}: ${c['cost']:.4f}"
            for c in cost_data
        ) if cost_data else "none"

        alert_str = ""
        if alerts:
            alert_str = "ALERTS: " + ", ".join(
                f"{a['agent_name']} at ${a['cost']:.2f}" for a in alerts
            )

        return self.call(user_message=(
            f"Standup data -- format it, nothing extra:\n"
            f"Campaigns: {campaign_count}\n"
            f"Tasks: {tasks_summary}\n"
            f"Costs: {cost_str}\n"
            f"{alert_str}"
        ))

    def campaign_wrapup(self, campaign_name: str, cost_data: dict, tasks_data: list) -> dict:
        return self.call(user_message=(
            f"Wrap-up for {campaign_name}. "
            f"Cost: {cost_data}. Tasks: {len(tasks_data)} completed. "
            f"2-3 sentences max."
        ))
