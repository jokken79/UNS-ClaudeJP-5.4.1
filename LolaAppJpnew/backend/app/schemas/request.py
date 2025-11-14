"""
Request (workflow) schemas for API requests and responses
"""
from datetime import date
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class RequestBase(BaseModel):
    """Base request schema"""
    request_type: str = Field(..., description="NYUSHA, YUKYU, TAISHA, TRANSFER")
    candidate_id: Optional[str] = Field(None, description="For NYUSHA requests")
    employee_id: Optional[int] = Field(None, gt=0, description="For YUKYU, TAISHA, TRANSFER requests")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Type-specific JSON data")
    notes: Optional[str] = None


class RequestCreate(RequestBase):
    """Schema for creating a request"""
    pass


class RequestUpdate(BaseModel):
    """Schema for updating a request (all fields optional)"""
    request_type: Optional[str] = None
    candidate_id: Optional[str] = None
    employee_id: Optional[int] = Field(None, gt=0)
    request_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class RequestResponse(RequestBase):
    """Schema for request response"""
    id: int
    status: str
    created_by: int
    created_at: date
    updated_at: Optional[date] = None
    approved_by: Optional[int] = None
    approved_at: Optional[date] = None
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True


class RequestListResponse(BaseModel):
    """Schema for request list response"""
    total: int
    skip: int
    limit: int
    requests: list[RequestResponse]


class RequestApprovalRequest(BaseModel):
    """Schema for approving/rejecting a request"""
    action: str = Field(..., description="APPROVE or REJECT")
    reason: Optional[str] = Field(None, description="Rejection reason (required for REJECT)")


class NyushaRequestData(BaseModel):
    """Type-specific data for NYUSHA (入社連絡票) requests"""
    line_id: int = Field(..., gt=0, description="Production line ID")
    hire_date: date = Field(..., description="Expected hire date")
    apartment_id: Optional[int] = Field(None, gt=0, description="Apartment assignment (optional)")
    notes: Optional[str] = None


class YukyuRequestData(BaseModel):
    """Type-specific data for YUKYU (有給休暇申請) requests"""
    start_date: date
    end_date: date
    days: float = Field(..., gt=0, description="Number of yukyu days to use")
    reason: Optional[str] = None


class TaishaRequestData(BaseModel):
    """Type-specific data for TAISHA (退社申請) requests"""
    resignation_date: date = Field(..., description="Last working day")
    reason: Optional[str] = None


class TransferRequestData(BaseModel):
    """Type-specific data for TRANSFER (配置転換) requests"""
    new_line_id: int = Field(..., gt=0, description="New production line ID")
    transfer_date: date = Field(..., description="Transfer effective date")
    reason: Optional[str] = None
