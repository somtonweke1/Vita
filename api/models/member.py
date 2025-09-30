"""
Pydantic models for Member API
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class GenderEnum(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class MemberStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    PENDING = "pending"


class RiskCategory(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


# Request Models

class AddressCreate(BaseModel):
    line1: str = Field(..., max_length=255)
    line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., max_length=10)
    country: str = Field(default="USA", max_length=3)


class HealthProfileCreate(BaseModel):
    height_cm: Optional[float] = Field(None, ge=50, le=250)
    weight_kg: Optional[float] = Field(None, ge=20, le=300)
    blood_pressure_systolic: Optional[int] = Field(None, ge=60, le=250)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=40, le=150)
    glucose_level: Optional[int] = Field(None, ge=40, le=600)
    cholesterol_total: Optional[int] = Field(None, ge=100, le=500)
    cholesterol_hdl: Optional[int] = Field(None, ge=20, le=150)
    cholesterol_ldl: Optional[int] = Field(None, ge=30, le=300)
    smoker: Optional[bool] = False
    alcohol_use: Optional[str] = Field(None, pattern="^(none|moderate|heavy)$")
    reported_stress_level: Optional[int] = Field(None, ge=1, le=10)


class MemberEnrollmentRequest(BaseModel):
    external_member_id: Optional[str] = Field(None, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: GenderEnum
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: AddressCreate
    enrollment_date: date
    monthly_premium: Decimal = Field(..., ge=0, decimal_places=2)
    initial_health_data: Optional[HealthProfileCreate] = None

    @validator('date_of_birth')
    def validate_age(cls, v):
        """Ensure member is at least 18 years old"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('Member must be at least 18 years old')
        if age > 120:
            raise ValueError('Invalid date of birth')
        return v


class MemberUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[AddressCreate] = None
    status: Optional[MemberStatus] = None


# Response Models

class AddressResponse(BaseModel):
    line1: str
    line2: Optional[str]
    city: str
    state: str
    zip_code: str
    country: str

    class Config:
        from_attributes = True


class HealthProfileResponse(BaseModel):
    height_cm: Optional[float]
    weight_kg: Optional[float]
    bmi: Optional[float]
    blood_pressure_systolic: Optional[int]
    blood_pressure_diastolic: Optional[int]
    glucose_level: Optional[int]
    cholesterol_total: Optional[int]
    cholesterol_hdl: Optional[int]
    cholesterol_ldl: Optional[int]
    smoker: Optional[bool]
    alcohol_use: Optional[str]
    reported_stress_level: Optional[int]
    last_updated: Optional[datetime]

    class Config:
        from_attributes = True


class MemberSummary(BaseModel):
    member_id: str
    full_name: str
    age: int
    risk_score: Optional[float]
    risk_category: Optional[RiskCategory]
    enrollment_date: date
    status: MemberStatus

    class Config:
        from_attributes = True


class MemberResponse(BaseModel):
    member_id: str
    external_member_id: Optional[str]
    first_name: str
    last_name: str
    date_of_birth: date
    age: int
    gender: GenderEnum
    email: EmailStr
    phone: Optional[str]
    address: Optional[AddressResponse]
    enrollment_date: date
    status: MemberStatus
    current_risk_score: Optional[float]
    current_risk_category: Optional[RiskCategory]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int


class MemberListResponse(BaseModel):
    data: List[MemberSummary]
    pagination: PaginationMeta


# Health Scoring Models

class RiskFactorResponse(BaseModel):
    factor_type: str
    factor_name: str
    contribution_points: float
    severity: str
    description: str
    recommended_action: str


class HealthScoreResponse(BaseModel):
    member_id: str
    score: float = Field(..., ge=1, le=100)
    risk_category: RiskCategory
    confidence_level: float = Field(..., ge=0, le=1)
    predicted_annual_cost: Decimal
    cost_prediction_range: dict  # {low: Decimal, high: Decimal}
    component_scores: dict  # demographic, clinical, behavioral, utilization
    top_risk_factors: List[RiskFactorResponse]
    recommended_interventions: List[str]
    calculation_timestamp: datetime
    model_version: str
    data_completeness_score: float

    class Config:
        from_attributes = True


class HealthScoreHistoryResponse(BaseModel):
    member_id: str
    scores: List[HealthScoreResponse]


# Error Response

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    error: dict  # {code: str, message: str, details: List[str]}