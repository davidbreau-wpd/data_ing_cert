CREATE TABLE IF NOT EXISTS service_reports_checklists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_category TEXT NULL, --
    item_number FLOAT NULL, --
    check_item TEX NULL, --
    result TEXT NULL,
    service_report_id INT NULL,
    order_number INT NULL
)