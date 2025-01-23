CREATE TABLE IF NOT EXISTS RAID_TRACKING (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    player_name TEXT NOT NULL,
    rank INTEGER NOT NULL,
    total_raided INTEGER NOT NULL,
    channel_id TEXT NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    is_personal BOOLEAN NOT NULL DEFAULT FALSE
);