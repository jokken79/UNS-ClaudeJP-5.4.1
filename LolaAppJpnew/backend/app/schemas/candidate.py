"""
Candidate schemas for API requests and responses
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class CandidateBase(BaseModel):
    """Base candidate schema"""
    full_name_kanji: str = Field(..., min_length=1, max_length=255)
    full_name_kana: Optional[str] = Field(None, max_length=255)
    full_name_roman: Optional[str] = Field(None, max_length=255)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    nationality: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema for creating a candidate"""
    rirekisho_id: str = Field(..., min_length=1, max_length=50)


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate"""
    full_name_kanji: Optional[str] = Field(None, min_length=1, max_length=255)
    full_name_kana: Optional[str] = Field(None, max_length=255)
    full_name_roman: Optional[str] = Field(None, max_length=255)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    nationality: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    status: Optional[str] = None


class CandidateResponse(CandidateBase):
    """Schema for candidate response"""
    rirekisho_id: str
    status: str
    created_at: date

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    """Schema for candidate list response"""
    total: int
    skip: int
    limit: int
    candidates: list[CandidateResponse]
