CREATE TABLE IF NOT EXISTS service_reports_metadatas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_company TEXT,
    wec_serial_number INT,
    order_number INT,
    order_type TEXT,
    start_date DATE NULL,
    end_date DATE NULL,
    completion_date DATE,
    free_of_defects INT NULL,
    defects INT NULL 
)

