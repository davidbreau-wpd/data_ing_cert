from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from uuid import UUID

if TYPE_CHECKING:
    from .service_report_metadata import ServiceReportMetadata
    from .service_report_checklist import ServiceReportChecklist

class IngestionTracking(SQLModel, table=True):
    __tablename__ = "ingestion_trackings"
    
    # COLUMNS
    service_report_uuid: UUID = Field(primary_key=True)
    file_name: str
    is_processed: bool = Field(default=False)
    has_error: bool = Field(default=False)
    processed_time: datetime | None = Field(default=None)
    
    # RELATIONSHIPS
    service_reports_metadatas: "ServiceReportMetadata" = Relationship(
        back_populates="ingestion_trackings",
        sa_relationship_kwargs={"foreign_keys": "ServiceReportMetadata.service_report_uuid"}
    )
    service_reports_checklists: list["ServiceReportChecklist"] = Relationship(
        back_populates="ingestion_trackings",
        sa_relationship_kwargs={"foreign_keys": "ServiceReportChecklist.service_report_uuid"}
    )