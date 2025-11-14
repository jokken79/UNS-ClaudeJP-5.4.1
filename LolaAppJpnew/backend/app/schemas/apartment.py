"""
Apartment schemas for API requests and responses
"""
from typing import Optional
from pydantic import BaseModel, Field


class ApartmentBase(BaseModel):
    """Base apartment schema"""
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_capacity: int = Field(..., gt=0)
    monthly_rent: float = Field(..., gt=0)
    utilities_included: bool = False
    deposit_required: float = Field(default=0.0, ge=0)
    room_type: Optional[str] = Field(None, max_length=100)


class ApartmentCreate(ApartmentBase):
    """Schema for creating an apartment"""
    pass


class ApartmentUpdate(BaseModel):
    """Schema for updating an apartment"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_capacity: Optional[int] = Field(None, gt=0)
    monthly_rent: Optional[float] = Field(None, gt=0)
    utilities_included: Optional[bool] = None
    is_available: Optional[bool] = None


class ApartmentResponse(ApartmentBase):
    """Schema for apartment response"""
    id: int
    current_occupancy: int
    is_available: bool

    class Config:
        from_attributes = True


class ApartmentListResponse(BaseModel):
    """Schema for apartment list response"""
    total: int
    skip: int
    limit: int
    apartments: list[ApartmentResponse]


class ApartmentRecommendation(BaseModel):
    """Schema for apartment recommendation"""
    apartment: ApartmentResponse
    score: float = Field(..., ge=0, le=100)
    proximity_score: float
    availability_score: float
    price_score: float
    compatibility_score: float
    transportation_score: float


class ApartmentRecommendationResponse(BaseModel):
    """Schema for apartment recommendations response"""
    employee_id: int
    recommendations: list[ApartmentRecommendation]
