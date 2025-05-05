ALTER TABLE ingestion_trackings

    ADD CONSTRAINT fk_service_reports_metadatas
        FOREIGN KEY (service_report_uuid)
        REFERENCES service_reports_metadatas(service_report_uuid),

    ADD CONSTRAINT fk_service_reports_checklists
        FOREIGN KEY (service_report_uuid)
        REFERENCES service_reports_checklists(service_report_uuid);