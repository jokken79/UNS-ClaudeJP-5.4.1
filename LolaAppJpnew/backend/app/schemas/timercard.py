"""
TimerCard schemas for API requests and responses
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class TimerCardBase(BaseModel):
    """Base timercard schema"""
    employee_id: int = Field(..., gt=0)
    work_date: date
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None
    break_minutes: int = Field(0, ge=0, description="Break time in minutes")
    regular_hours: float = Field(0.0, ge=0)
    overtime_hours: float = Field(0.0, ge=0)
    night_hours: float = Field(0.0, ge=0)
    holiday_hours: float = Field(0.0, ge=0)


class TimerCardCreate(TimerCardBase):
    """Schema for creating a timercard"""
    pass


class TimerCardUpdate(BaseModel):
    """Schema for updating a timercard (all fields optional)"""
    employee_id: Optional[int] = Field(None, gt=0)
    work_date: Optional[date] = None
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None
    break_minutes: Optional[int] = Field(None, ge=0)
    regular_hours: Optional[float] = Field(None, ge=0)
    overtime_hours: Optional[float] = Field(None, ge=0)
    night_hours: Optional[float] = Field(None, ge=0)
    holiday_hours: Optional[float] = Field(None, ge=0)


class TimerCardResponse(TimerCardBase):
    """Schema for timercard response"""
    id: int
    ocr_processed: bool
    ocr_confidence: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class TimerCardListResponse(BaseModel):
    """Schema for timercard list response"""
    total: int
    skip: int
    limit: int
    timercards: list[TimerCardResponse]


class TimerCardOCRRequest(BaseModel):
    """Schema for OCR processing request"""
    employee_id: int = Field(..., gt=0, description="Employee hakenmoto_id")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, le=2100, description="Year")
