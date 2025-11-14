"""
Plant schemas for API requests and responses
"""
from typing import Optional
from pydantic import BaseModel, Field


class PlantBase(BaseModel):
    """Base plant schema"""
    company_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    default_work_hours: Optional[str] = Field(None, max_length=500, description="e.g., 昼勤：7時00分～15時30分")
    default_break_time: Optional[str] = Field(None, max_length=500)
    default_overtime_limit: Optional[str] = Field(None, max_length=500, description="e.g., 3時間/日、42時間/月")
    notes: Optional[str] = None


class PlantCreate(PlantBase):
    """Schema for creating a plant"""
    pass


class PlantUpdate(BaseModel):
    """Schema for updating a plant (all fields optional)"""
    company_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    default_work_hours: Optional[str] = Field(None, max_length=500)
    default_break_time: Optional[str] = Field(None, max_length=500)
    default_overtime_limit: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class PlantResponse(PlantBase):
    """Schema for plant response"""
    id: int

    class Config:
        from_attributes = True


class PlantListResponse(BaseModel):
    """Schema for plant list response"""
    total: int
    skip: int
    limit: int
    plants: list[PlantResponse]
