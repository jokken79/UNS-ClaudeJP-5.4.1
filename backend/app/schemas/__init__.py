"""
Pydantic Schemas for UNS-ClaudeJP 5.2

This module exports all Pydantic models for request/response validation.
Use: from app.schemas import CandidateCreate, EmployeeResponse

Organized by functional module:
- Authentication: User, login, registration schemas
- Candidates: Candidate management and OCR schemas
- Employees: Employee management schemas
- Factories: Factory/client site schemas
- Timer Cards: Attendance tracking schemas
- Salary: Payroll calculation schemas
- Requests: Leave request workflow schemas
- Dashboard: Analytics and statistics schemas
- Base/Common: Shared base schemas, pagination, responses
"""

# Authentication schemas
from app.schemas.auth import (
    UserLogin,
    UserRegister,
    Token,
    TokenData,
    UserResponse,
    UserUpdate,
    PasswordChange,
)

# Base/Common schemas
from app.schemas.base import (
    ResponseBase,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse,
)

# Response schemas
from app.schemas.responses import (
    BaseResponse,
    OCRData,
    OCRResponse,
    CacheStatsResponse,
)

# Candidate schemas
from app.schemas.candidate import (
    CandidateBase,
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    DocumentUpload,
    CandidateApprove,
    CandidateReject,
    RirekishoFormCreate,
    CandidateFormResponse,
)

# Employee schemas
from app.schemas.employee import (
    EmployeeBase,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeTerminate,
    YukyuUpdate,
)

# Factory schemas
from app.schemas.factory import (
    FactoryBase,
    FactoryCreate,
    FactoryUpdate,
    FactoryResponse,
    FactoryConfig,
    FactoryStats,
)

# Timer Card schemas
from app.schemas.timer_card import (
    TimerCardBase,
    TimerCardCreate,
    TimerCardUpdate,
    TimerCardResponse,
    TimerCardBulkCreate,
    TimerCardProcessResult,
    TimerCardOCRData,
    TimerCardUploadResponse,
    TimerCardApprove,
)

# Salary schemas
from app.schemas.salary import (
    SalaryCalculationBase,
    SalaryCalculate,
    SalaryCalculationResponse,
    SalaryBulkCalculate,
    SalaryBulkResult,
    SalaryMarkPaid,
    SalaryReport,
    SalaryStatistics,
)

# Request schemas
from app.schemas.request import (
    RequestBase,
    RequestCreate,
    RequestUpdate,
    RequestResponse,
    RequestReview,
    RequestStats,
    IkkikokokuRequest,
    TaishaRequest,
)

# Dashboard schemas
from app.schemas.dashboard import (
    DashboardStats,
    FactoryDashboard,
    EmployeeAlert,
    MonthlyTrend,
    TopPerformer,
    RecentActivity,
    AdminDashboard,
    EmployeeDashboard,
    CoordinatorDashboard,
)

# Settings schemas
from app.schemas.settings import (
    VisibilityToggleResponse,
    VisibilityToggleUpdate,
    SystemSettingResponse,
)

# Yukyu (有給休暇 - Paid Vacation) schemas
from app.schemas.yukyu import (
    YukyuBalanceBase,
    YukyuBalanceCreate,
    YukyuBalanceUpdate,
    YukyuBalanceResponse,
    YukyuBalanceSummary,
    YukyuRequestBase,
    YukyuRequestCreate,
    YukyuRequestUpdate,
    YukyuRequestApprove,
    YukyuRequestReject,
    YukyuRequestResponse,
    YukyuUsageDetailBase,
    YukyuUsageDetailCreate,
    YukyuUsageDetailResponse,
    YukyuCalculationRequest,
    YukyuCalculationResponse,
    YukyuReport,
    YukyuAlert,
    EmployeeByFactoryResponse,
)

__all__ = [
    # Authentication
    "UserLogin",
    "UserRegister",
    "Token",
    "TokenData",
    "UserResponse",
    "UserUpdate",
    "PasswordChange",

    # Base/Common
    "ResponseBase",
    "ErrorResponse",
    "PaginationParams",
    "PaginatedResponse",

    # Responses
    "BaseResponse",
    "OCRData",
    "OCRResponse",
    "CacheStatsResponse",

    # Candidates
    "CandidateBase",
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    "DocumentUpload",
    "CandidateApprove",
    "CandidateReject",
    "RirekishoFormCreate",
    "CandidateFormResponse",

    # Employees
    "EmployeeBase",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "EmployeeTerminate",
    "YukyuUpdate",

    # Factories
    "FactoryBase",
    "FactoryCreate",
    "FactoryUpdate",
    "FactoryResponse",
    "FactoryConfig",
    "FactoryStats",

    # Timer Cards
    "TimerCardBase",
    "TimerCardCreate",
    "TimerCardUpdate",
    "TimerCardResponse",
    "TimerCardBulkCreate",
    "TimerCardProcessResult",
    "TimerCardOCRData",
    "TimerCardUploadResponse",
    "TimerCardApprove",

    # Salary
    "SalaryCalculationBase",
    "SalaryCalculate",
    "SalaryCalculationResponse",
    "SalaryBulkCalculate",
    "SalaryBulkResult",
    "SalaryMarkPaid",
    "SalaryReport",
    "SalaryStatistics",

    # Requests
    "RequestBase",
    "RequestCreate",
    "RequestUpdate",
    "RequestResponse",
    "RequestReview",
    "RequestStats",
    "IkkikokokuRequest",
    "TaishaRequest",

    # Dashboard
    "DashboardStats",
    "FactoryDashboard",
    "EmployeeAlert",
    "MonthlyTrend",
    "TopPerformer",
    "RecentActivity",
    "AdminDashboard",
    "EmployeeDashboard",
    "CoordinatorDashboard",

    # Settings
    "VisibilityToggleResponse",
    "VisibilityToggleUpdate",
    "SystemSettingResponse",

    # Yukyu (有給休暇 - Paid Vacation)
    "YukyuBalanceBase",
    "YukyuBalanceCreate",
    "YukyuBalanceUpdate",
    "YukyuBalanceResponse",
    "YukyuBalanceSummary",
    "YukyuRequestBase",
    "YukyuRequestCreate",
    "YukyuRequestUpdate",
    "YukyuRequestApprove",
    "YukyuRequestReject",
    "YukyuRequestResponse",
    "YukyuUsageDetailBase",
    "YukyuUsageDetailCreate",
    "YukyuUsageDetailResponse",
    "YukyuCalculationRequest",
    "YukyuCalculationResponse",
    "YukyuReport",
    "YukyuAlert",
    "EmployeeByFactoryResponse",
]
