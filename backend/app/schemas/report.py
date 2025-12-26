"""
Report Schemas

Pydantic schemas for report-related operations
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.report import ReportReason, ReportStatus


class ReportCreate(BaseModel):
    """Schema for creating a new report"""
    review_id: int = Field(..., gt=0)
    reason: ReportReason
    description: Optional[str] = Field(None, max_length=1000)


class ReportResponse(BaseModel):
    """Schema for report response"""
    id: int
    review_id: int
    user_id: int
    reason: ReportReason
    description: Optional[str]
    status: ReportStatus
    created_at: datetime
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
