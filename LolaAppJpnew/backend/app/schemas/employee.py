"""
Employee schemas for API requests and responses
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class EmployeeBase(BaseModel):
    """Base employee schema"""
    rirekisho_id: str = Field(..., max_length=50)
    full_name_kanji: str = Field(..., min_length=1, max_length=255)
    full_name_kana: Optional[str] = Field(None, max_length=255)
    line_id: int = Field(..., gt=0)
    jikyu: int = Field(..., gt=0, description="Hourly wage in yen")
    contract_type: str = Field(..., max_length=20)
    hire_date: date


class EmployeeCreate(EmployeeBase):
    """Schema for creating an employee"""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee"""
    full_name_kanji: Optional[str] = Field(None, min_length=1, max_length=255)
    full_name_kana: Optional[str] = Field(None, max_length=255)
    line_id: Optional[int] = Field(None, gt=0)
    jikyu: Optional[int] = Field(None, gt=0)
    apartment_id: Optional[int] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    status: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """Schema for employee response"""
    hakenmoto_id: int
    status: str
    apartment_id: Optional[int] = None
    created_at: date

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Schema for employee list response"""
    total: int
    skip: int
    limit: int
    employees: list[EmployeeResponse]


class AssignFactoryRequest(BaseModel):
    """Schema for assigning employee to factory"""
    line_id: int = Field(..., gt=0)


class AssignApartmentRequest(BaseModel):
    """Schema for assigning apartment"""
    apartment_id: Optional[int] = Field(None, gt=0, description="Apartment ID or None for auto-assign")
