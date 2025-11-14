"""
Company schemas for API requests and responses
"""
from typing import Optional
from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """Base company schema"""
    name: str = Field(..., min_length=1, max_length=255)
    name_kana: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    default_closing_date: Optional[int] = Field(None, ge=1, le=31, description="締め日 (1-31)")
    default_payment_date: Optional[int] = Field(None, ge=0, le=31, description="支払日 (0=month end, 1-31)")
    notes: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema for creating a company"""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_kana: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    default_closing_date: Optional[int] = Field(None, ge=1, le=31)
    default_payment_date: Optional[int] = Field(None, ge=0, le=31)
    notes: Optional[str] = None


class CompanyResponse(CompanyBase):
    """Schema for company response"""
    id: int

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Schema for company list response"""
    total: int
    skip: int
    limit: int
    companies: list[CompanyResponse]
