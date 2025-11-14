"""
Line (production line) schemas for API requests and responses
"""
from typing import Optional
from pydantic import BaseModel, Field


class LineBase(BaseModel):
    """Base line schema"""
    plant_id: int = Field(..., gt=0)
    line_number: Optional[str] = Field(None, max_length=50, description="e.g., Factory-39")
    name: str = Field(..., min_length=1, max_length=255, description="e.g., リフト作業")
    description: Optional[str] = None
    hourly_rate: float = Field(..., gt=0, description="Base hourly wage in JPY")


class LineCreate(LineBase):
    """Schema for creating a line"""
    pass


class LineUpdate(BaseModel):
    """Schema for updating a line (all fields optional)"""
    plant_id: Optional[int] = Field(None, gt=0)
    line_number: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, gt=0)


class LineResponse(LineBase):
    """Schema for line response"""
    id: int

    class Config:
        from_attributes = True


class LineListResponse(BaseModel):
    """Schema for line list response"""
    total: int
    skip: int
    limit: int
    lines: list[LineResponse]
