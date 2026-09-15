-- REASON: Every time a rule fires, we log it here. Grafana can plot
-- this as a timeline of automation activity. This is the "flight
-- recorder" for the engine.

CREATE TABLE IF NOT EXISTS automation_events (
    id             SERIAL PRIMARY KEY,
    occurred_at    TIMESTAMPTZ DEFAULT now(),
    rule_name      TEXT NOT NULL,
    severity       TEXT NOT NULL,             -- info | warning | critical
    metric         TEXT NOT NULL,
    observed_value NUMERIC,
    threshold      NUMERIC,
    comparator     TEXT,
    message        TEXT,
    action_taken   TEXT,
    action_status  TEXT,                      -- success | failed | skipped
    action_detail  TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_occurred
    ON automation_events (occurred_at DESC);

-- REASON: Stores the last known state of each rule so we can fire on
-- the RISING EDGE only — no alert storm while a condition stays true.
CREATE TABLE IF NOT EXISTS automation_state (
    rule_name     TEXT PRIMARY KEY,
    is_active     BOOLEAN NOT NULL DEFAULT false,
    last_fired_at TIMESTAMPTZ,
    last_value    NUMERIC,
    updated_at    TIMESTAMPTZ DEFAULT now()
);
