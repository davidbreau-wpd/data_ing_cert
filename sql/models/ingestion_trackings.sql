CREATE TABLE IF NOT EXISTS ingestion_trackings (
    service_report_uuid TEXT PRIMARY KEY,
    file_name TEXT,
    is_processed BOOLEAN DEFAULT FALSE,
    has_error BOOLEAN DEFAULT FALSE,
    processed_time TIMESTAMP
);