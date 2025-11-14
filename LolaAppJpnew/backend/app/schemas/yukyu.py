"""
Yukyu (paid vacation) schemas for API requests and responses
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class YukyuGrantRequest(BaseModel):
    """Schema for granting yukyu"""
    employee_id: int = Field(..., gt=0)
    fiscal_year: int = Field(..., ge=2020, le=2100)
    granted_days: float = Field(..., gt=0, le=40)
    grant_date: Optional[date] = None
    reason: Optional[str] = None


class YukyuUseRequest(BaseModel):
    """Schema for using yukyu"""
    employee_id: int = Field(..., gt=0)
    days_to_use: float = Field(..., gt=0)
    usage_date: date
    start_date: date
    end_date: date
    reason: Optional[str] = None


class YukyuBalanceResponse(BaseModel):
    """Schema for yukyu balance response"""
    id: int
    employee_id: int
    fiscal_year: int
    granted_days: float
    used_days: float
    remaining_days: float
    grant_date: date
    expiry_date: date
    is_expired: bool

    class Config:
        from_attributes = True


class YukyuTransactionResponse(BaseModel):
    """Schema for yukyu transaction response"""
    id: int
    balance_id: int
    employee_id: int
    transaction_type: str
    transaction_date: date
    days: float
    description: Optional[str]

    class Config:
        from_attributes = True


class YukyuSummaryResponse(BaseModel):
    """Schema for yukyu summary"""
    employee_id: int
    employee_name: str
    total_granted: float
    total_used: float
    total_remaining: float
    balances: list[YukyuBalanceResponse]
    recent_transactions: list[YukyuTransactionResponse]


class YukyuAutoGrantRequest(BaseModel):
    """Schema for auto-granting yukyu to all employees"""
    fiscal_year: int = Field(..., ge=2020, le=2100)
    grant_date: Optional[date] = None
