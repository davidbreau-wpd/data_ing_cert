from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID
from datetime import date

if TYPE_CHECKING:
    from .service_report_checklists import ServiceReportChecklist
    from .ingestion_trackings import IngestionTracking

class ServiceReportMetadata(SQLModel, table=True):
    __tablename__ = "service_reports_metadatas"
    
    # COLUMNS
    service_report_uuid: UUID = Field(primary_key=True)
    order_number: int
    service_company: str
    wec_serial_number: int
    order_type: str
    completion_date: date
    free_of_defects: int | None = Field(default=None)
    defects: int | None = Field(default=None)
    
    # RELATIONSHIPS
    service_reports_checklists: list["ServiceReportChecklist"] = Relationship(
        back_populates="service_reports_metadatas",
        sa_relationship_kwargs={
            "foreign_keys": "[ServiceReportChecklist.service_report_uuid, ServiceReportChecklist.order_number, ServiceReportChecklist.service_company]"
        }
    )
    ingestion_trackings: "IngestionTracking" = Relationship(
        back_populates="service_reports_metadatas"
    )