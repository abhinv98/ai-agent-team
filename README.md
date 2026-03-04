# AI Marketing Team

Six Claude-powered agents collaborating in Slack with human-in-the-loop approval and a live dashboard.

## Agents

| Agent | Role | Model |
|-------|------|-------|
| Maya | CMO / Strategist | claude-sonnet-4-6 |
| Ananya | Copywriter | claude-sonnet-4-6 |
| Priya | SEO + Research | claude-sonnet-4-6 |
| Ramesh | Social Media | claude-sonnet-4-6 |
| Subodh | Data Analyst | claude-sonnet-4-6 |
| Kavya | Project Manager | claude-haiku-4-5 |

## Setup

1. Copy `.env.example` to `.env` and fill in credentials
2. Run `db/schema.sql` in Supabase SQL Editor
3. Install Python dependencies: `pip install -r requirements.txt`
4. Install frontend: `cd dashboard/frontend && npm install`
5. Start: `python main.py`

## Slack Commands

- `/campaign <brief>` — Start a new campaign
- `/standup` — Trigger daily standup summary
- `/costs` — Show today's cost summary

## Dashboard

The React dashboard runs on port 3000 (dev) or is served by FastAPI at port 8000 (production).

- **Kanban Board** — Drag-and-drop task management across 6 status columns
- **Cost Tracker** — Per-agent cost charts with daily/cumulative views
- **Campaigns** — Campaign list with task breakdowns

## Research-First Workflow

Every campaign follows: Research (Priya + Subodh) → Content (Ananya) → Distribution (Ramesh) → Wrap-up (Kavya). Each phase requires human approval before the next begins. All approved outputs are stored in the knowledge base for future reference.

## Deploy

```bash
docker build -t ai-marketing-team .
docker run -p 8000:8000 --env-file .env ai-marketing-team
```

Or deploy to Railway with `railway up`.
