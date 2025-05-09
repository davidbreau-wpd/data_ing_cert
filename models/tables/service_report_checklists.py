from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID

if TYPE_CHECKING:
    from .service_report_metadata import ServiceReportMetadata
    from .ingestion_trackings import IngestionTracking

class ServiceReportChecklist(SQLModel, table=True):
    __tablename__ = "service_reports_checklists"
    
    # COLUMNS
    id: int | None = Field(default=None, primary_key=True)  
    service_report_uuid: UUID = Field()  
    order_number: int | None = Field(default=None)
    line_number: int | None = Field(default=None)
    service_company: str | None = Field(default=None)
    item_category: str | None = Field(default=None)
    item_number: float | None = Field(default=None)
    check_item: str | None = Field(default=None)
    result: str | None = Field(default=None)
    
    # RELATIONSHIPS
    service_reports_metadatas: "ServiceReportMetadata" = Relationship(
        back_populates="service_reports_checklists",
        sa_relationship_kwargs={
            "foreign_keys": "[service_report_uuid, order_number, service_company]"
        }
    )
    ingestion_trackings: "IngestionTracking" = Relationship(
        back_populates="service_reports_checklists",
        sa_relationship_kwargs={
            "foreign_keys": "service_report_uuid"
        }
    )