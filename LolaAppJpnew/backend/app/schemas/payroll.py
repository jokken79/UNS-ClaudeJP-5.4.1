"""
Payroll schemas for API requests and responses
"""
from typing import Optional
from pydantic import BaseModel, Field


class PayrollCalculationRequest(BaseModel):
    """Schema for payroll calculation request"""
    employee_id: int = Field(..., gt=0, description="Employee hakenmoto_id")
    year: int = Field(..., ge=2020, le=2100, description="Year")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")


class PayrollCalculationResponse(BaseModel):
    """Schema for payroll calculation response"""
    employee_id: int
    employee_name: str
    year: int
    month: int

    # Hours summary
    total_regular_hours: float
    total_overtime_hours: float
    total_night_hours: float
    total_holiday_hours: float
    total_yukyu_days: float

    # Pay breakdown
    regular_pay: float
    overtime_pay: float
    night_pay: float
    holiday_pay: float
    yukyu_pay: float
    gross_pay: float

    # Deductions
    apartment_rent: float
    social_insurance: float
    health_insurance: float
    pension_insurance: float
    employment_insurance: float
    income_tax: float
    total_deductions: float

    # Final pay
    net_pay: float

    # Metadata
    hourly_rate: float
    days_worked: int
    notes: Optional[str] = None


class PayrollBatchCalculationRequest(BaseModel):
    """Schema for batch payroll calculation"""
    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)
    employee_ids: Optional[list[int]] = Field(None, description="Specific employee IDs or None for all active")


class PayrollBatchCalculationResponse(BaseModel):
    """Schema for batch payroll calculation response"""
    year: int
    month: int
    total_employees: int
    success_count: int
    error_count: int
    total_gross_pay: float
    total_net_pay: float
    results: list[PayrollCalculationResponse]
