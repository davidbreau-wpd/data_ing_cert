CREATE TABLE IF NOT EXISTS ingestion_trackings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT,
    status TEXT,
    processed_time DATETIME,
)