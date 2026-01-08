"""
Report Schemas

Pydantic schemas for report validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.report import ReportReason, ReportStatus
from app.core.sanitizer import sanitize_text


class ReportCreate(BaseModel):
    """Schema for creating a report"""
    review_id: int
    reason: ReportReason
    description: Optional[str] = Field(None, max_length=1000)

    @classmethod
    def validate_description(cls, v):
        """Sanitize description text"""
        if v:
            return sanitize_text(v, max_length=1000)
        return v


class ReportResponse(BaseModel):
    """Schema for report response"""
    id: int
    user_id: int
    review_id: int
    reason: ReportReason
    description: Optional[str]
    status: ReportStatus
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True
