CREATE TABLE IF NOT EXISTS ANALYTICS(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    app TEXT NOT NULL,
    full_command TEXT NOT NULL,
    discord_user_id INTEGER NOT NULL,
    discord_user_name TEXT NOT NULL,
    discord_server_id INTEGER NOT NULL,
    discord_server_name TEXT NOT NULL,
    travian_server_code TEXT NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    execution_time_ms INTEGER
); 