CREATE TABLE IF NOT EXISTS ingestion_trackings (
    service_report_uuid INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT,
    status TEXT,
    processed_time TIMESTAMP
);