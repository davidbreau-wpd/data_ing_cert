CREATE TABLE IF NOT EXISTS service_reports_metadatas (
    service_report_uuid TEXT PRIMARY KEY,
    order_number INT,
    service_company TEXT,
    wec_serial_number INT,
    order_type TEXT,
    completion_date DATE,
    free_of_defects INT NULL,
    defects INT NULL 
)