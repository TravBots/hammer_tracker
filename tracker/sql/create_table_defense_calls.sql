CREATE TABLE IF NOT EXISTS DEFENSE_CALLS(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    created_by_id INTEGER NOT NULL,
    created_by_name TEXT NOT NULL,
    land_time TIMESTAMP NOT NULL, 
    x_coordinate INTEGER NOT NULL, 
    y_coordinate INTEGER NOT NULL, 
    amount_requested INTEGER NOT NULL, 
    amount_submitted INTEGER,
    created_at TIMESTAMP NOT NULL, 
    updated_at TIMESTAMP
    );
