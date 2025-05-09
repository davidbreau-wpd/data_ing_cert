ALTER TABLE ingestion_trackings

    ADD CONSTRAINT FK_service_reports_metadatas__ingestion_trackings
        FOREIGN KEY (service_report_uuid)
        REFERENCES service_reports_metadatas(service_report_uuid),

    ADD CONSTRAINT FK_service_reports_checklists__ingestion_trackings
        FOREIGN KEY (service_report_uuid)
        REFERENCES service_reports_checklists(service_report_uuid);

    -- ADD CONSTRAINT unique_file
    --     UNIQUE (file_name);
        
    -- ADD CONSTRAINT valid_processed_time
    --     CHECK (
    --         (is_processed = TRUE AND processed_time IS NOT NULL) OR
    --         (is_processed = FALSE AND processed_time IS NULL)
    --     );