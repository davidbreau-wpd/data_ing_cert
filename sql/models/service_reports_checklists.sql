CREATE TABLE IF NOT EXISTS service_reports_checklists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_report_uuid INTEGER NOT NULL,
    order_number INT NULL,
    line_number INTEGER NULL,
    service_company TEXT NULL,
    item_category TEXT NULL, --
    item_number FLOAT NULL, --
    check_item TEXT NULL, --
    result TEXT NULL
)