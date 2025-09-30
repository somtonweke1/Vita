"""
Health Scoring API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta
from decimal import Decimal
import logging

from api.database import get_db, AuditLogger
from api.models.member import (
    HealthScoreResponse,
    HealthScoreHistoryResponse,
    RiskFactorResponse,
    RiskCategory
)
from api.dependencies.auth import get_current_user
from services.analytics.health_scoring.scoring_engine import (
    HealthScoringEngine,
    MemberHealthData,
    RiskFactor
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health-scores", tags=["Health Scoring"])


@router.get(
    "/{member_id}",
    response_model=HealthScoreResponse,
    summary="Get current health score"
)
async def get_current_health_score(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve most recent health risk score for member.

    Returns:
    - Overall score (1-100, lower = healthier)
    - Risk category (low, moderate, high, critical)
    - Predicted annual healthcare cost
    - Top 5 risk factors with recommendations
    - Recommended interventions

    Audit logged: Yes (PHI access)
    """
    try:
        # Log access
        AuditLogger.log_access(
            user_id=current_user.get('sub', 'unknown'),
            action='access',
            table_name='health_risk_scores',
            record_id=member_id,
            member_id=member_id,
            success=True
        )

        # In production: query latest score from database
        # latest_score = db.query(HealthRiskScore)\
        #     .filter(HealthRiskScore.member_id == member_id)\
        #     .order_by(HealthRiskScore.calculation_timestamp.desc())\
        #     .first()
        #
        # if not latest_score:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"No health score found for member {member_id}"
        #     )

        # Mock response for demonstration
        return HealthScoreResponse(
            member_id=member_id,
            score=72.5,
            risk_category=RiskCategory.HIGH,
            confidence_level=0.85,
            predicted_annual_cost=Decimal('14200.00'),
            cost_prediction_range={
                'low': Decimal('8520.00'),
                'high': Decimal('19880.00')
            },
            component_scores={
                'demographic': 35.0,
                'clinical': 85.0,
                'behavioral': 65.0,
                'utilization': 72.0
            },
            top_risk_factors=[
                RiskFactorResponse(
                    factor_type='chronic_disease',
                    factor_name='Type 2 Diabetes',
                    contribution_points=25.0,
                    severity='high',
                    description='Diagnosed with Type 2 Diabetes (E11.9)',
                    recommended_action='Enroll in diabetes management program'
                ),
                RiskFactorResponse(
                    factor_type='biometric',
                    factor_name='Uncontrolled hypertension',
                    contribution_points=15.0,
                    severity='high',
                    description='BP 145/92 mmHg',
                    recommended_action='Immediate physician follow-up, medication review'
                ),
                RiskFactorResponse(
                    factor_type='behavioral',
                    factor_name='Physical inactivity',
                    contribution_points=15.0,
                    severity='medium',
                    description='Average 3200 steps/day (target: 7000+)',
                    recommended_action='Gradual increase in daily activity, consider fitness coaching'
                )
            ],
            recommended_interventions=[
                'Enroll in chronic disease management program',
                'Schedule comprehensive care coordination visit within 7 days',
                'Medication therapy management consultation',
                'Start graduated walking program (goal: 7000 steps/day)'
            ],
            calculation_timestamp=datetime.utcnow(),
            model_version='1.0.0',
            data_completeness_score=0.78
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get health score for {member_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health score"
        )


@router.post(
    "/{member_id}",
    response_model=HealthScoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate health score"
)
async def calculate_health_score(
    member_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger new health risk score calculation for member.

    This endpoint:
    1. Gathers member data (demographics, health profile, claims, wearables)
    2. Runs health scoring engine
    3. Stores results in database
    4. Triggers intervention recommendations if high risk
    5. Returns calculated score

    For large calculations, returns 202 Accepted with job_id for async processing.

    Requires: write:health_data scope
    """
    try:
        # In production: gather comprehensive member data
        # member = db.query(Member).filter(Member.member_id == member_id).first()
        # if not member:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Member {member_id} not found"
        #     )
        #
        # health_profile = db.query(HealthProfile).filter(
        #     HealthProfile.member_id == member_id
        # ).first()
        #
        # # Get claims data
        # claims = db.query(Claim).filter(
        #     Claim.member_id == member_id,
        #     Claim.service_date >= date.today() - timedelta(days=365)
        # ).all()
        #
        # # Get wearable data (last 30 days)
        # wearable_data = db.query(WearableMetric).filter(
        #     WearableMetric.member_id == member_id,
        #     WearableMetric.recorded_timestamp >= datetime.utcnow() - timedelta(days=30)
        # ).all()

        # Initialize scoring engine
        engine = HealthScoringEngine()

        # Create member health data (mock for demo)
        member_data = MemberHealthData(
            member_id=member_id,
            age=45,
            gender='M',
            bmi=30.0,
            blood_pressure_systolic=145,
            blood_pressure_diastolic=92,
            glucose_level=128,
            cholesterol_ldl=155,
            avg_daily_steps=3200,
            avg_sleep_hours=6.5,
            chronic_conditions=['E11.9', 'I10'],  # Diabetes, Hypertension
            medications=['Metformin', 'Lisinopril'],
            total_claims_cost=Decimal('8500'),
            emergency_visits=2,
            primary_care_visits=3,
            smoker=False,
            alcohol_use='moderate',
            reported_stress_level=7,
            has_primary_care_physician=True
        )

        # Calculate score
        logger.info(f"Calculating health score for member {member_id}")
        score_result = engine.calculate_score(member_data)

        # In production: save to database
        # health_score = HealthRiskScore(
        #     member_id=member_id,
        #     calculation_timestamp=score_result.calculation_timestamp,
        #     overall_score=score_result.score,
        #     risk_category=score_result.risk_category.value,
        #     predicted_annual_cost=score_result.predicted_annual_cost,
        #     model_version=score_result.model_version,
        #     ...
        # )
        # db.add(health_score)
        # db.commit()

        # If high risk, trigger intervention recommendations in background
        if score_result.risk_category.value in ['high', 'critical']:
            logger.info(f"Member {member_id} is high risk, queuing intervention recommendations")
            # background_tasks.add_task(generate_intervention_recommendations, member_id, db)

        # Log calculation
        AuditLogger.log_access(
            user_id=current_user.get('sub', 'unknown'),
            action='create',
            table_name='health_risk_scores',
            record_id=member_id,
            member_id=member_id,
            success=True,
            details={'score': float(score_result.score), 'risk_category': score_result.risk_category.value}
        )

        # Convert to API response format
        return HealthScoreResponse(
            member_id=score_result.member_id,
            score=score_result.score,
            risk_category=RiskCategory(score_result.risk_category.value),
            confidence_level=score_result.confidence_level,
            predicted_annual_cost=score_result.predicted_annual_cost,
            cost_prediction_range={
                'low': score_result.cost_prediction_range[0],
                'high': score_result.cost_prediction_range[1]
            },
            component_scores=score_result.calculation_metadata['component_scores'],
            top_risk_factors=[
                RiskFactorResponse(
                    factor_type=rf.factor_type.value,
                    factor_name=rf.factor_name,
                    contribution_points=rf.contribution_points,
                    severity=rf.severity,
                    description=rf.description,
                    recommended_action=rf.recommended_action
                ) for rf in score_result.top_risk_factors
            ],
            recommended_interventions=score_result.recommended_interventions,
            calculation_timestamp=score_result.calculation_timestamp,
            model_version=score_result.model_version,
            data_completeness_score=score_result.data_completeness_score
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate health score for {member_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate health score"
        )


@router.get(
    "/{member_id}/history",
    response_model=HealthScoreHistoryResponse,
    summary="Get score history"
)
async def get_health_score_history(
    member_id: str,
    start_date: date = Query(None),
    end_date: date = Query(None),
    interval: str = Query('monthly', regex='^(daily|weekly|monthly)$'),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve time-series of historical health scores for trend analysis.

    Query parameters:
    - start_date: Filter scores from this date (default: 1 year ago)
    - end_date: Filter scores until this date (default: today)
    - interval: Sampling interval (daily, weekly, monthly)

    Returns array of scores ordered by calculation_timestamp DESC.

    Useful for:
    - Member portal to show progress over time
    - Analytics to identify improvement/decline trends
    - Validate intervention effectiveness
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365)

        # In production: query time-series data
        # Using TimescaleDB's time_bucket for efficient aggregation
        # if interval == 'monthly':
        #     scores = db.query(HealthRiskScore)\
        #         .filter(
        #             HealthRiskScore.member_id == member_id,
        #             HealthRiskScore.calculation_timestamp >= start_date,
        #             HealthRiskScore.calculation_timestamp <= end_date
        #         )\
        #         .order_by(HealthRiskScore.calculation_timestamp.desc())\
        #         .all()

        # Mock historical data showing improvement trend
        mock_scores = [
            HealthScoreResponse(
                member_id=member_id,
                score=72.5,
                risk_category=RiskCategory.HIGH,
                confidence_level=0.85,
                predicted_annual_cost=Decimal('14200.00'),
                cost_prediction_range={'low': Decimal('8520.00'), 'high': Decimal('19880.00')},
                component_scores={'demographic': 35.0, 'clinical': 85.0, 'behavioral': 65.0, 'utilization': 72.0},
                top_risk_factors=[],
                recommended_interventions=[],
                calculation_timestamp=datetime.utcnow(),
                model_version='1.0.0',
                data_completeness_score=0.78
            ),
            HealthScoreResponse(
                member_id=member_id,
                score=75.0,
                risk_category=RiskCategory.HIGH,
                confidence_level=0.82,
                predicted_annual_cost=Decimal('15100.00'),
                cost_prediction_range={'low': Decimal('9060.00'), 'high': Decimal('21140.00')},
                component_scores={'demographic': 35.0, 'clinical': 88.0, 'behavioral': 68.0, 'utilization': 75.0},
                top_risk_factors=[],
                recommended_interventions=[],
                calculation_timestamp=datetime.utcnow() - timedelta(days=90),
                model_version='1.0.0',
                data_completeness_score=0.75
            )
        ]

        return HealthScoreHistoryResponse(
            member_id=member_id,
            scores=mock_scores
        )

    except Exception as e:
        logger.error(f"Failed to get score history for {member_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve score history"
        )