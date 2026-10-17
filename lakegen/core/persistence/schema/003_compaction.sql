CREATE TABLE IF NOT EXISTS compactions (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    data TEXT NOT NULL,
    last_compacted_turn_id UUID NOT NULL REFERENCES agent_turns(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS compactions_session_created_at_idx
    ON compactions (session_id, created_at DESC);