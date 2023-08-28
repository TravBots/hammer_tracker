CREATE TABLE IF NOT EXISTS SUBMITTED_DEFENSE(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    defense_call_id INTEGER NOT NULL,
    submitted_by_id INTEGER NOT NULL,
    submitted_by_name TEXT NOT NULL, 
    amount_submitted INTEGER NOT NULL, 
    submitted_at TIMESTAMP NOT NULL,
    FOREIGN KEY(defense_call_id) REFERENCES SUBMITTED_DEFENSE(id)
    );
