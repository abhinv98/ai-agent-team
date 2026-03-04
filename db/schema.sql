-- ============================================================
-- AI Marketing Team — Full Database Schema
-- Run this in Supabase SQL Editor
-- ============================================================

-- Campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    brief TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks (Kanban items)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    assigned_agent TEXT NOT NULL,
    status TEXT DEFAULT 'backlog' CHECK (status IN ('backlog', 'in_progress', 'pending_review', 'changes_requested', 'approved', 'done')),
    priority INTEGER DEFAULT 0,
    depends_on UUID[] DEFAULT '{}',
    output_content TEXT,
    feedback TEXT,
    approved_by TEXT,
    approved_at TIMESTAMPTZ,
    slack_message_ts TEXT,
    slack_channel TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent cost logs (every single API call)
CREATE TABLE agent_costs (
    id BIGSERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_write_tokens INTEGER DEFAULT 0,
    estimated_cost_usd DECIMAL(10, 6) NOT NULL,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent activity log (for live feed)
CREATE TABLE agent_activity (
    id BIGSERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    channel TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stores every human-approved agent output for future reference
CREATE TABLE agent_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    category TEXT NOT NULL,
    topic TEXT NOT NULL,
    niche TEXT,
    input_context TEXT,
    approved_output TEXT NOT NULL,
    feedback_history JSONB DEFAULT '[]',
    tags TEXT[] DEFAULT '{}',
    approved_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stores raw research data from each research phase
CREATE TABLE research_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    agent_name TEXT NOT NULL,
    research_type TEXT NOT NULL,
    source TEXT,
    niche TEXT NOT NULL,
    raw_data JSONB,
    summary TEXT NOT NULL,
    key_insights TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stores Facebook Ad Library snapshots for trend analysis
CREATE TABLE ad_library_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    niche TEXT NOT NULL,
    query_term TEXT NOT NULL,
    ad_count INTEGER,
    top_ads JSONB,
    trends JSONB,
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_campaign ON tasks(campaign_id);
CREATE INDEX idx_tasks_agent ON tasks(assigned_agent);
CREATE INDEX idx_costs_agent ON agent_costs(agent_name);
CREATE INDEX idx_costs_date ON agent_costs(created_at);
CREATE INDEX idx_activity_date ON agent_activity(created_at);
CREATE INDEX idx_knowledge_agent ON agent_knowledge(agent_name);
CREATE INDEX idx_knowledge_topic ON agent_knowledge(topic);
CREATE INDEX idx_knowledge_niche ON agent_knowledge(niche);
CREATE INDEX idx_knowledge_tags ON agent_knowledge USING GIN(tags);
CREATE INDEX idx_research_niche ON research_findings(niche);
CREATE INDEX idx_research_type ON research_findings(research_type);
CREATE INDEX idx_adlib_niche ON ad_library_snapshots(niche);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER campaigns_updated_at BEFORE UPDATE ON campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
