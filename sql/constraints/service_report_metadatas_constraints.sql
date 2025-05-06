ALTER TABLE service_reports_metadatas

    ADD CONSTRAINT FK_service_reports_checklists__service_reports_metadatas
        FOREIGN KEY (service_report_uuid, order_number, service_company)
        REFERENCES service_reports_checklists(service_report_uuid, order_number, service_company),
    
    ADD CONSTRAINT FK_ingestion_trackings__service_reports_metadatas
        FOREIGN KEY (service_report_uuid)
        REFERENCES ingestion_trackings(service_report_uuid);