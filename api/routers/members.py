"""
Member Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import logging

from api.database import get_db, AuditLogger
from api.models.member import (
    MemberEnrollmentRequest,
    MemberResponse,
    MemberSummary,
    MemberUpdateRequest,
    MemberListResponse,
    PaginationMeta,
    HealthProfileResponse,
    HealthProfileCreate,
    MemberStatus,
    RiskCategory
)
from api.dependencies.auth import get_current_user
from services.analytics.health_scoring.scoring_engine import (
    HealthScoringEngine,
    MemberHealthData
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/members", tags=["Members"])


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll new member"
)
async def create_member(
    member_data: MemberEnrollmentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create new member enrollment.

    Requires: write:members scope

    Steps:
    1. Validate enrollment data
    2. Create member record
    3. Create health profile (if provided)
    4. Calculate initial health risk score
    5. Create policy with specified premium
    6. Log audit trail
    """
    try:
        # Check for duplicate email
        # In production: query database for existing email
        # existing = db.query(Member).filter(Member.email == member_data.email).first()
        # if existing:
        #     raise HTTPException(
        #         status_code=status.HTTP_409_CONFLICT,
        #         detail="Member with this email already exists"
        #     )

        # Create member (pseudo-code - actual DB operations)
        member_id = f"M{date.today().strftime('%Y%m%d')}{12345}"  # Generate unique ID

        # Calculate age
        today = date.today()
        age = today.year - member_data.date_of_birth.year - (
            (today.month, today.day) < (member_data.date_of_birth.month, member_data.date_of_birth.day)
        )

        # If initial health data provided, calculate risk score
        initial_risk_score = None
        initial_risk_category = None

        if member_data.initial_health_data:
            try:
                scoring_engine = HealthScoringEngine()

                # Convert to scoring engine format
                health_data = MemberHealthData(
                    member_id=member_id,
                    age=age,
                    gender=member_data.gender.value,
                    bmi=None,  # Calculate from height/weight if provided
                    smoker=member_data.initial_health_data.smoker or False,
                    alcohol_use=member_data.initial_health_data.alcohol_use or "none",
                    reported_stress_level=member_data.initial_health_data.reported_stress_level
                )

                score_result = scoring_engine.calculate_score(health_data)
                initial_risk_score = score_result.score
                initial_risk_category = score_result.risk_category.value

                logger.info(
                    f"Calculated initial risk score for new member: {initial_risk_score} "
                    f"({initial_risk_category})"
                )

            except Exception as e:
                logger.error(f"Failed to calculate initial risk score: {e}", exc_info=True)
                # Don't fail enrollment if scoring fails

        # Log audit trail
        AuditLogger.log_access(
            user_id=current_user.get('sub', 'unknown'),
            action='create',
            table_name='members',
            record_id=member_id,
            member_id=member_id,
            success=True,
            details={'enrollment_date': str(member_data.enrollment_date)}
        )

        # Return mock response (in production, return actual DB record)
        return MemberResponse(
            member_id=member_id,
            external_member_id=member_data.external_member_id,
            first_name=member_data.first_name,
            last_name=member_data.last_name,
            date_of_birth=member_data.date_of_birth,
            age=age,
            gender=member_data.gender,
            email=member_data.email,
            phone=member_data.phone,
            address=member_data.address,
            enrollment_date=member_data.enrollment_date,
            status=MemberStatus.ACTIVE,
            current_risk_score=initial_risk_score,
            current_risk_category=initial_risk_category,
            created_at=date.today(),
            updated_at=date.today()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create member: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create member enrollment"
        )


@router.get(
    "",
    response_model=MemberListResponse,
    summary="List members"
)
async def list_members(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status_filter: Optional[MemberStatus] = Query(None, alias="status"),
    risk_category_filter: Optional[RiskCategory] = Query(None, alias="risk_category"),
    sort_by: str = Query("enrollment_date", regex="^(enrollment_date|risk_score|last_name)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve paginated list of members with optional filters.

    Requires: read:members scope

    Query parameters:
    - page: Page number (default: 1)
    - page_size: Records per page (default: 50, max: 100)
    - status: Filter by member status
    - risk_category: Filter by risk category
    - sort_by: Sort field (enrollment_date, risk_score, last_name)
    """
    try:
        # In production: build SQLAlchemy query with filters and pagination
        # query = db.query(Member)
        #
        # if status_filter:
        #     query = query.filter(Member.status == status_filter)
        #
        # if risk_category_filter:
        #     query = query.filter(Member.current_risk_category == risk_category_filter)
        #
        # # Apply sorting
        # if sort_by == "risk_score":
        #     query = query.order_by(Member.current_risk_score.desc())
        # elif sort_by == "last_name":
        #     query = query.order_by(Member.last_name)
        # else:
        #     query = query.order_by(Member.enrollment_date.desc())
        #
        # # Get total count
        # total_records = query.count()
        #
        # # Apply pagination
        # offset = (page - 1) * page_size
        # members = query.offset(offset).limit(page_size).all()

        # Mock data for demonstration
        mock_members = [
            MemberSummary(
                member_id="M001",
                full_name="John Doe",
                age=45,
                risk_score=72.5,
                risk_category=RiskCategory.HIGH,
                enrollment_date=date(2024, 1, 15),
                status=MemberStatus.ACTIVE
            ),
            MemberSummary(
                member_id="M002",
                full_name="Jane Smith",
                age=32,
                risk_score=35.2,
                risk_category=RiskCategory.MODERATE,
                enrollment_date=date(2024, 2, 1),
                status=MemberStatus.ACTIVE
            )
        ]

        total_records = 2
        total_pages = (total_records + page_size - 1) // page_size

        return MemberListResponse(
            data=mock_members,
            pagination=PaginationMeta(
                page=page,
                page_size=page_size,
                total_records=total_records,
                total_pages=total_pages
            )
        )

    except Exception as e:
        logger.error(f"Failed to list members: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve member list"
        )


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get member details"
)
async def get_member(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve detailed information for a specific member.

    Requires: read:members scope

    Audit logged: Yes (PHI access)
    """
    try:
        # In production: query database
        # member = db.query(Member).filter(Member.member_id == member_id).first()
        # if not member:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Member {member_id} not found"
        #     )

        # Log PHI access
        AuditLogger.log_access(
            user_id=current_user.get('sub', 'unknown'),
            action='access',
            table_name='members',
            record_id=member_id,
            member_id=member_id,
            success=True
        )

        # Mock response
        if member_id == "M001":
            return MemberResponse(
                member_id="M001",
                external_member_id="EXT12345",
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1979, 5, 15),
                age=45,
                gender="M",
                email="john.doe@example.com",
                phone="555-0123",
                address=None,
                enrollment_date=date(2024, 1, 15),
                status=MemberStatus.ACTIVE,
                current_risk_score=72.5,
                current_risk_category=RiskCategory.HIGH,
                created_at=date(2024, 1, 15),
                updated_at=date.today()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member {member_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get member {member_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve member"
        )


@router.patch(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Update member information"
)
async def update_member(
    member_id: str,
    update_data: MemberUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update member contact information or status.

    Requires: write:members scope

    Audit logged: Yes (PHI modification)
    """
    try:
        # In production: update database record
        # member = db.query(Member).filter(Member.member_id == member_id).first()
        # if not member:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Member {member_id} not found"
        #     )
        #
        # # Apply updates
        # if update_data.email:
        #     member.email = update_data.email
        # if update_data.phone:
        #     member.phone = update_data.phone
        # if update_data.status:
        #     member.status = update_data.status
        #
        # db.commit()
        # db.refresh(member)

        # Log modification
        AuditLogger.log_access(
            user_id=current_user.get('sub', 'unknown'),
            action='modify',
            table_name='members',
            record_id=member_id,
            member_id=member_id,
            success=True,
            details=update_data.dict(exclude_unset=True)
        )

        # Return updated member (mock)
        return await get_member(member_id, db, current_user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update member {member_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update member"
        )


@router.get(
    "/{member_id}/health-profile",
    response_model=HealthProfileResponse,
    summary="Get member health profile"
)
async def get_health_profile(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve member's health profile including biometrics, conditions, medications.

    Requires: read:health_data scope

    Audit logged: Yes (PHI access)
    """
    try:
        # Log PHI access
        AuditLogger.log_access(
            user_id=current_user.get('sub', 'unknown'),
            action='access',
            table_name='member_health_profiles',
            record_id=member_id,
            member_id=member_id,
            success=True
        )

        # Mock response
        return HealthProfileResponse(
            height_cm=178.0,
            weight_kg=95.0,
            bmi=30.0,
            blood_pressure_systolic=145,
            blood_pressure_diastolic=92,
            glucose_level=128,
            cholesterol_total=220,
            cholesterol_hdl=42,
            cholesterol_ldl=155,
            smoker=False,
            alcohol_use="moderate",
            reported_stress_level=7,
            last_updated=date.today()
        )

    except Exception as e:
        logger.error(f"Failed to get health profile for {member_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health profile"
        )