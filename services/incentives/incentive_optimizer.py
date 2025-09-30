"""
VitaNexus Prevention Incentive Optimization System

Intelligent algorithm for determining optimal wellness intervention investments
per member based on ROI, responsiveness, and resource constraints.

This is the core of VitaNexus's prevention-first strategy - investing smartly
in keeping members healthy to maximize both member wellness and company profitability.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class IncentiveType(Enum):
    """Types of incentives for wellness behaviors"""
    PREMIUM_REDUCTION = "premium_reduction"  # Reduce monthly premium
    CASH_REWARD = "cash_reward"  # Direct payment
    HSA_CONTRIBUTION = "hsa_contribution"  # Health Savings Account credit
    POINTS = "points"  # Redeemable points for products
    PROGRAM_DISCOUNT = "program_discount"  # Discount on wellness programs
    GIFT_CARD = "gift_card"  # Retail gift cards


class BehaviorCategory(Enum):
    """Categories of wellness behaviors to incentivize"""
    PREVENTIVE_SCREENING = "preventive_screening"  # Annual physicals, screenings
    ACTIVITY_GOALS = "activity_goals"  # Steps, exercise minutes
    PROGRAM_COMPLETION = "program_completion"  # Finish wellness program
    BIOMETRIC_IMPROVEMENT = "biometric_improvement"  # Weight loss, BP control
    MEDICATION_ADHERENCE = "medication_adherence"  # Take meds as prescribed
    HEALTH_ASSESSMENT = "health_assessment"  # Complete health questionnaire
    CHRONIC_DISEASE_MANAGEMENT = "chronic_disease_management"  # Attend care visits
    MENTAL_HEALTH_ENGAGEMENT = "mental_health_engagement"  # Counseling attendance


@dataclass
class MemberResponsiveness:
    """Model of how responsive a member is to different incentives"""
    member_id: str

    # Historical engagement
    previous_incentives_received: int = 0
    previous_incentives_acted_on: int = 0
    incentive_response_rate: float = 0.5  # 0-1

    # Behavioral indicators
    self_motivated: bool = False  # Engages without incentives
    needs_nudging: bool = True  # Responds well to incentives
    high_inertia: bool = False  # Hard to motivate

    # Preferences (learned over time)
    preferred_incentive_types: List[IncentiveType] = field(default_factory=list)
    minimum_effective_incentive_amount: Decimal = Decimal('25')

    # Demographics affecting responsiveness
    age: int = 0
    income_bracket: str = "middle"  # 'low', 'middle', 'high'
    health_literacy_level: str = "medium"  # 'low', 'medium', 'high'


@dataclass
class IncentiveOffer:
    """An incentive offer for a specific behavior"""
    offer_id: str
    member_id: str

    behavior_category: BehaviorCategory
    behavior_description: str

    # Incentive details
    incentive_type: IncentiveType
    incentive_amount: Decimal

    # Goal criteria
    goal_metric: str  # e.g., "steps_per_day", "weight_loss_lbs"
    goal_target: float
    goal_duration_days: int

    # Timeline
    offer_date: date
    expiration_date: date

    # Expected outcomes
    probability_of_completion: float  # 0-1
    expected_health_impact: float  # Risk score reduction
    expected_cost_avoidance: Decimal

    # ROI
    incentive_cost: Decimal
    expected_roi: float  # Percentage
    priority_score: float

    # Status
    status: str = "offered"  # 'offered', 'accepted', 'in_progress', 'completed', 'expired'
    acceptance_date: Optional[date] = None
    completion_date: Optional[date] = None


@dataclass
class IncentiveBudget:
    """Budget allocation for incentive programs"""
    total_budget: Decimal
    budget_period: str  # 'monthly', 'quarterly', 'annual'

    # Allocation by category
    category_budgets: Dict[BehaviorCategory, Decimal] = field(default_factory=dict)

    # Constraints
    max_per_member_per_period: Decimal = Decimal('500')
    min_roi_threshold: float = 2.0  # Minimum 200% ROI

    # Tracking
    spent_to_date: Decimal = Decimal('0')
    committed_to_date: Decimal = Decimal('0')  # Offered but not yet paid
    available_budget: Decimal = field(init=False)

    def __post_init__(self):
        self.available_budget = self.total_budget - self.spent_to_date - self.committed_to_date


@dataclass
class IncentivePerformanceMetrics:
    """Track performance of incentive programs"""
    behavior_category: BehaviorCategory
    incentive_type: IncentiveType

    # Volumes
    offers_made: int = 0
    offers_accepted: int = 0
    offers_completed: int = 0

    # Rates
    acceptance_rate: float = 0.0
    completion_rate: float = 0.0

    # Financial
    total_cost: Decimal = Decimal('0')
    total_cost_avoidance: Decimal = Decimal('0')
    avg_roi: float = 0.0

    # Health impact
    avg_risk_reduction: float = 0.0
    members_impacted: int = 0


class IncentiveOptimizer:
    """
    Core optimization engine for prevention incentive allocation.

    Determines:
    1. Which members to incentivize
    2. Which behaviors to target
    3. What incentive type and amount
    4. Expected ROI and priority
    """

    def __init__(self, budget: IncentiveBudget):
        self.budget = budget

        # Learned parameters (would be ML models in production)
        self.behavior_base_costs = {
            BehaviorCategory.PREVENTIVE_SCREENING: Decimal('50'),
            BehaviorCategory.ACTIVITY_GOALS: Decimal('100'),
            BehaviorCategory.PROGRAM_COMPLETION: Decimal('200'),
            BehaviorCategory.BIOMETRIC_IMPROVEMENT: Decimal('250'),
            BehaviorCategory.MEDICATION_ADHERENCE: Decimal('150'),
            BehaviorCategory.HEALTH_ASSESSMENT: Decimal('25'),
            BehaviorCategory.CHRONIC_DISEASE_MANAGEMENT: Decimal('300'),
            BehaviorCategory.MENTAL_HEALTH_ENGAGEMENT: Decimal('175'),
        }

        # Expected health impact (risk score reduction points)
        self.behavior_health_impact = {
            BehaviorCategory.PREVENTIVE_SCREENING: 3.0,
            BehaviorCategory.ACTIVITY_GOALS: 8.0,
            BehaviorCategory.PROGRAM_COMPLETION: 12.0,
            BehaviorCategory.BIOMETRIC_IMPROVEMENT: 15.0,
            BehaviorCategory.MEDICATION_ADHERENCE: 10.0,
            BehaviorCategory.HEALTH_ASSESSMENT: 1.0,
            BehaviorCategory.CHRONIC_DISEASE_MANAGEMENT: 20.0,
            BehaviorCategory.MENTAL_HEALTH_ENGAGEMENT: 9.0,
        }

        # Cost avoidance per risk point (from financial model)
        self.cost_per_risk_point = Decimal('580')

        # Performance tracking
        self.performance_metrics: Dict[Tuple[BehaviorCategory, IncentiveType], IncentivePerformanceMetrics] = {}

    def identify_high_value_targets(
        self,
        members: List[Dict],  # Member data with risk scores
        responsiveness: Dict[str, MemberResponsiveness]
    ) -> List[str]:
        """
        Identify members who are high-value targets for incentives.

        High value = high risk (cost) + high responsiveness + not already engaged

        Args:
            members: List of member data dictionaries
            responsiveness: Mapping of member_id to responsiveness profile

        Returns:
            List of member_ids prioritized for incentive targeting
        """
        scored_members = []

        for member in members:
            member_id = member['member_id']
            risk_score = member.get('current_risk_score', 50)
            predicted_cost = member.get('predicted_annual_cost', Decimal('5800'))
            active_programs = member.get('active_program_count', 0)

            # Get responsiveness
            resp = responsiveness.get(member_id, MemberResponsiveness(member_id=member_id))

            # Calculate value score
            # Higher risk = more cost savings potential
            risk_factor = risk_score / 100

            # Higher responsiveness = more likely to act
            response_factor = resp.incentive_response_rate

            # Not already in programs = capacity for engagement
            engagement_factor = 1.0 if active_programs == 0 else 0.5

            # Avoid over-incentivizing self-motivated members (waste of money)
            motivation_factor = 0.3 if resp.self_motivated else 1.0

            value_score = (
                float(predicted_cost) * risk_factor * response_factor *
                engagement_factor * motivation_factor
            )

            scored_members.append({
                'member_id': member_id,
                'value_score': value_score,
                'risk_score': risk_score,
                'predicted_cost': predicted_cost
            })

        # Sort by value score
        scored_members.sort(key=lambda x: x['value_score'], reverse=True)

        return [m['member_id'] for m in scored_members]

    def recommend_behavior_for_member(
        self,
        member_data: Dict,
        member_responsiveness: MemberResponsiveness,
        top_risk_factors: List[Dict]
    ) -> BehaviorCategory:
        """
        Determine which behavior to incentivize for a member.

        Matches member's top risk factors to most impactful behaviors.

        Args:
            member_data: Member health and demographic data
            member_responsiveness: Member's responsiveness profile
            top_risk_factors: List of member's top risk factors

        Returns:
            BehaviorCategory to target
        """
        # Map risk factors to behavior categories
        risk_to_behavior_map = {
            'chronic_disease': BehaviorCategory.CHRONIC_DISEASE_MANAGEMENT,
            'physical_inactivity': BehaviorCategory.ACTIVITY_GOALS,
            'obesity': BehaviorCategory.BIOMETRIC_IMPROVEMENT,
            'uncontrolled_hypertension': BehaviorCategory.BIOMETRIC_IMPROVEMENT,
            'medication_nonadherence': BehaviorCategory.MEDICATION_ADHERENCE,
            'no_preventive_care': BehaviorCategory.PREVENTIVE_SCREENING,
            'mental_health': BehaviorCategory.MENTAL_HEALTH_ENGAGEMENT,
        }

        # Score each potential behavior
        behavior_scores = defaultdict(float)

        for risk_factor in top_risk_factors[:3]:  # Top 3 risk factors
            factor_type = risk_factor.get('factor_type', '')
            contribution = risk_factor.get('contribution_points', 0)

            # Map to behavior
            if factor_type in risk_to_behavior_map:
                behavior = risk_to_behavior_map[factor_type]
                behavior_scores[behavior] += contribution

        # If no specific risk factors, default to general prevention
        if not behavior_scores:
            if member_data.get('last_checkup_days_ago', 9999) > 365:
                return BehaviorCategory.PREVENTIVE_SCREENING
            else:
                return BehaviorCategory.ACTIVITY_GOALS

        # Return highest scoring behavior
        return max(behavior_scores.items(), key=lambda x: x[1])[0]

    def calculate_optimal_incentive(
        self,
        member_responsiveness: MemberResponsiveness,
        behavior: BehaviorCategory,
        expected_health_impact: float,
        expected_cost_avoidance: Decimal
    ) -> Tuple[IncentiveType, Decimal]:
        """
        Calculate optimal incentive type and amount.

        Balances:
        - Member's incentive preferences and minimum effective amount
        - Cost of incentive vs. expected benefit
        - ROI requirements

        Returns:
            (incentive_type, incentive_amount)
        """
        # Start with member's minimum effective incentive
        base_amount = member_responsiveness.minimum_effective_incentive_amount

        # Adjust based on behavior difficulty
        difficulty_multipliers = {
            BehaviorCategory.HEALTH_ASSESSMENT: Decimal('0.5'),  # Easy
            BehaviorCategory.PREVENTIVE_SCREENING: Decimal('0.8'),
            BehaviorCategory.ACTIVITY_GOALS: Decimal('1.5'),  # Sustained effort
            BehaviorCategory.MEDICATION_ADHERENCE: Decimal('1.3'),
            BehaviorCategory.BIOMETRIC_IMPROVEMENT: Decimal('2.0'),  # Hard
            BehaviorCategory.PROGRAM_COMPLETION: Decimal('1.8'),
            BehaviorCategory.CHRONIC_DISEASE_MANAGEMENT: Decimal('1.6'),
            BehaviorCategory.MENTAL_HEALTH_ENGAGEMENT: Decimal('1.4'),
        }

        difficulty_mult = difficulty_multipliers.get(behavior, Decimal('1.0'))
        calculated_amount = base_amount * difficulty_mult

        # Ensure ROI threshold is met
        # ROI = (cost_avoidance - incentive_cost) / incentive_cost
        # incentive_cost must be < cost_avoidance / (1 + min_roi)
        max_affordable_incentive = expected_cost_avoidance / (Decimal('1') + Decimal(str(self.budget.min_roi_threshold)))
        calculated_amount = min(calculated_amount, max_affordable_incentive)

        # Cap at per-member limit
        calculated_amount = min(calculated_amount, self.budget.max_per_member_per_period)

        # Round to nearest $5 for simplicity
        calculated_amount = (calculated_amount / 5).quantize(Decimal('1')) * 5

        # Determine incentive type based on member preference and amount
        if member_responsiveness.preferred_incentive_types:
            incentive_type = member_responsiveness.preferred_incentive_types[0]
        else:
            # Default logic based on amount and demographics
            if calculated_amount >= Decimal('100'):
                incentive_type = IncentiveType.PREMIUM_REDUCTION  # Most valuable
            elif calculated_amount >= Decimal('50'):
                incentive_type = IncentiveType.CASH_REWARD
            else:
                incentive_type = IncentiveType.HSA_CONTRIBUTION

        return (incentive_type, calculated_amount)

    def create_incentive_offer(
        self,
        member_id: str,
        member_data: Dict,
        member_responsiveness: MemberResponsiveness,
        behavior: BehaviorCategory,
        incentive_type: IncentiveType,
        incentive_amount: Decimal
    ) -> IncentiveOffer:
        """
        Create a complete incentive offer for a member.

        Args:
            member_id: Member identifier
            member_data: Member health and demographic data
            member_responsiveness: Member's responsiveness profile
            behavior: Target behavior
            incentive_type: Type of incentive
            incentive_amount: Amount of incentive

        Returns:
            IncentiveOffer ready to present to member
        """
        # Define goal based on behavior
        goal_definitions = {
            BehaviorCategory.PREVENTIVE_SCREENING: {
                'description': 'Complete annual physical exam and recommended screenings',
                'metric': 'preventive_visits',
                'target': 1.0,
                'duration_days': 60
            },
            BehaviorCategory.ACTIVITY_GOALS: {
                'description': 'Walk 10,000 steps per day for 30 days',
                'metric': 'avg_daily_steps',
                'target': 10000.0,
                'duration_days': 30
            },
            BehaviorCategory.PROGRAM_COMPLETION: {
                'description': 'Complete assigned wellness program',
                'metric': 'program_completion',
                'target': 1.0,
                'duration_days': 90
            },
            BehaviorCategory.BIOMETRIC_IMPROVEMENT: {
                'description': 'Reduce BMI by 2 points or reach healthy BMI',
                'metric': 'bmi_reduction',
                'target': 2.0,
                'duration_days': 180
            },
            BehaviorCategory.MEDICATION_ADHERENCE: {
                'description': 'Maintain 90%+ medication adherence for 90 days',
                'metric': 'medication_adherence_rate',
                'target': 0.90,
                'duration_days': 90
            },
            BehaviorCategory.HEALTH_ASSESSMENT: {
                'description': 'Complete comprehensive health risk assessment',
                'metric': 'assessment_completion',
                'target': 1.0,
                'duration_days': 14
            },
            BehaviorCategory.CHRONIC_DISEASE_MANAGEMENT: {
                'description': 'Attend all scheduled disease management visits',
                'metric': 'visit_attendance_rate',
                'target': 1.0,
                'duration_days': 180
            },
            BehaviorCategory.MENTAL_HEALTH_ENGAGEMENT: {
                'description': 'Attend 6 counseling sessions',
                'metric': 'counseling_sessions',
                'target': 6.0,
                'duration_days': 120
            }
        }

        goal_def = goal_definitions[behavior]

        # Calculate expected outcomes
        expected_health_impact = self.behavior_health_impact[behavior]
        expected_cost_avoidance = Decimal(str(expected_health_impact)) * self.cost_per_risk_point

        # Probability of completion (from member responsiveness and behavior difficulty)
        base_prob = member_responsiveness.incentive_response_rate
        difficulty_adjustment = {
            BehaviorCategory.HEALTH_ASSESSMENT: 0.9,
            BehaviorCategory.PREVENTIVE_SCREENING: 0.85,
            BehaviorCategory.ACTIVITY_GOALS: 0.7,
            BehaviorCategory.MEDICATION_ADHERENCE: 0.75,
            BehaviorCategory.PROGRAM_COMPLETION: 0.65,
            BehaviorCategory.MENTAL_HEALTH_ENGAGEMENT: 0.70,
            BehaviorCategory.BIOMETRIC_IMPROVEMENT: 0.55,
            BehaviorCategory.CHRONIC_DISEASE_MANAGEMENT: 0.80,
        }
        probability = base_prob * difficulty_adjustment.get(behavior, 0.7)

        # ROI calculation
        incentive_cost = incentive_amount
        expected_benefit = expected_cost_avoidance * Decimal(str(probability))
        roi = float((expected_benefit - incentive_cost) / incentive_cost * 100) if incentive_cost > 0 else 0.0

        # Priority score (higher = should do first)
        priority_score = float(expected_benefit) * probability / float(incentive_cost) if incentive_cost > 0 else 0.0

        # Timeline
        offer_date = date.today()
        expiration_date = offer_date + timedelta(days=30)  # 30 days to accept

        offer = IncentiveOffer(
            offer_id=f"INC-{member_id}-{behavior.value}-{offer_date.isoformat()}",
            member_id=member_id,
            behavior_category=behavior,
            behavior_description=goal_def['description'],
            incentive_type=incentive_type,
            incentive_amount=incentive_amount,
            goal_metric=goal_def['metric'],
            goal_target=goal_def['target'],
            goal_duration_days=goal_def['duration_days'],
            offer_date=offer_date,
            expiration_date=expiration_date,
            probability_of_completion=probability,
            expected_health_impact=expected_health_impact,
            expected_cost_avoidance=expected_cost_avoidance,
            incentive_cost=incentive_cost,
            expected_roi=roi,
            priority_score=priority_score
        )

        return offer

    def optimize_incentive_portfolio(
        self,
        members: List[Dict],
        responsiveness: Dict[str, MemberResponsiveness],
        top_risk_factors: Dict[str, List[Dict]]
    ) -> List[IncentiveOffer]:
        """
        Create optimal portfolio of incentive offers across member population.

        Uses greedy algorithm to maximize expected value within budget constraints.

        Args:
            members: List of member data
            responsiveness: Mapping of member_id to responsiveness profile
            top_risk_factors: Mapping of member_id to their top risk factors

        Returns:
            List of IncentiveOffers that maximize ROI within budget
        """
        logger.info(f"Optimizing incentive portfolio for {len(members)} members")
        logger.info(f"Available budget: ${self.budget.available_budget:,.2f}")

        # Step 1: Identify high-value target members
        target_members = self.identify_high_value_targets(members, responsiveness)

        # Step 2: Generate candidate offers for top targets
        candidate_offers = []

        for member_id in target_members:
            # Find member data
            member_data = next((m for m in members if m['member_id'] == member_id), None)
            if not member_data:
                continue

            resp = responsiveness.get(member_id, MemberResponsiveness(member_id=member_id))
            risk_factors = top_risk_factors.get(member_id, [])

            # Determine best behavior to target
            behavior = self.recommend_behavior_for_member(member_data, resp, risk_factors)

            # Calculate expected impact
            expected_health_impact = self.behavior_health_impact[behavior]
            expected_cost_avoidance = Decimal(str(expected_health_impact)) * self.cost_per_risk_point

            # Calculate optimal incentive
            incentive_type, incentive_amount = self.calculate_optimal_incentive(
                resp, behavior, expected_health_impact, expected_cost_avoidance
            )

            # Create offer
            offer = self.create_incentive_offer(
                member_id, member_data, resp, behavior, incentive_type, incentive_amount
            )

            # Only include if ROI meets threshold
            if offer.expected_roi >= (self.budget.min_roi_threshold * 100):
                candidate_offers.append(offer)

        # Step 3: Sort by priority score and select within budget
        candidate_offers.sort(key=lambda x: x.priority_score, reverse=True)

        selected_offers = []
        remaining_budget = self.budget.available_budget

        for offer in candidate_offers:
            if remaining_budget >= offer.incentive_cost:
                selected_offers.append(offer)
                remaining_budget -= offer.incentive_cost

                logger.info(
                    f"Selected offer for {offer.member_id}: {offer.behavior_category.value} "
                    f"- ${offer.incentive_amount:,.2f} incentive, "
                    f"{offer.expected_roi:.0f}% expected ROI"
                )

        logger.info(
            f"Optimized portfolio: {len(selected_offers)} offers, "
            f"${self.budget.available_budget - remaining_budget:,.2f} allocated, "
            f"${remaining_budget:,.2f} remaining"
        )

        # Calculate portfolio-level expected outcomes
        total_expected_cost_avoidance = sum(
            o.expected_cost_avoidance * Decimal(str(o.probability_of_completion))
            for o in selected_offers
        )
        total_incentive_cost = sum(o.incentive_cost for o in selected_offers)
        portfolio_roi = float((total_expected_cost_avoidance - total_incentive_cost) / total_incentive_cost * 100) if total_incentive_cost > 0 else 0.0

        logger.info(
            f"Portfolio expected outcomes: "
            f"${total_expected_cost_avoidance:,.2f} cost avoidance, "
            f"{portfolio_roi:.0f}% ROI"
        )

        return selected_offers


# Example usage
if __name__ == "__main__":
    # Set up budget
    budget = IncentiveBudget(
        total_budget=Decimal('50000'),
        budget_period='monthly',
        max_per_member_per_period=Decimal('500'),
        min_roi_threshold=2.0
    )

    # Sample members
    members = [
        {
            'member_id': 'M001',
            'current_risk_score': 72,
            'predicted_annual_cost': Decimal('14200'),
            'active_program_count': 0,
            'last_checkup_days_ago': 450
        },
        {
            'member_id': 'M002',
            'current_risk_score': 45,
            'predicted_annual_cost': Decimal('7200'),
            'active_program_count': 0,
            'last_checkup_days_ago': 200
        },
        {
            'member_id': 'M003',
            'current_risk_score': 88,
            'predicted_annual_cost': Decimal('22000'),
            'active_program_count': 1,
            'last_checkup_days_ago': 90
        },
    ]

    # Responsiveness profiles
    responsiveness = {
        'M001': MemberResponsiveness(
            member_id='M001',
            incentive_response_rate=0.7,
            needs_nudging=True,
            preferred_incentive_types=[IncentiveType.PREMIUM_REDUCTION],
            minimum_effective_incentive_amount=Decimal('75')
        ),
        'M002': MemberResponsiveness(
            member_id='M002',
            incentive_response_rate=0.85,
            self_motivated=True,
            preferred_incentive_types=[IncentiveType.CASH_REWARD],
            minimum_effective_incentive_amount=Decimal('50')
        ),
        'M003': MemberResponsiveness(
            member_id='M003',
            incentive_response_rate=0.5,
            high_inertia=True,
            preferred_incentive_types=[IncentiveType.CASH_REWARD],
            minimum_effective_incentive_amount=Decimal('150')
        ),
    }

    # Risk factors
    top_risk_factors = {
        'M001': [
            {'factor_type': 'chronic_disease', 'contribution_points': 25},
            {'factor_type': 'physical_inactivity', 'contribution_points': 15}
        ],
        'M002': [
            {'factor_type': 'no_preventive_care', 'contribution_points': 10}
        ],
        'M003': [
            {'factor_type': 'chronic_disease', 'contribution_points': 40},
            {'factor_type': 'medication_nonadherence', 'contribution_points': 20}
        ]
    }

    # Run optimizer
    optimizer = IncentiveOptimizer(budget)
    offers = optimizer.optimize_incentive_portfolio(members, responsiveness, top_risk_factors)

    # Display results
    print(f"\n{'='*80}")
    print("INCENTIVE PORTFOLIO OPTIMIZATION RESULTS")
    print(f"{'='*80}\n")

    print(f"Budget: ${budget.total_budget:,.2f}")
    print(f"Offers Generated: {len(offers)}\n")

    for i, offer in enumerate(offers, 1):
        print(f"{i}. Member {offer.member_id}")
        print(f"   Behavior: {offer.behavior_category.value}")
        print(f"   Goal: {offer.behavior_description}")
        print(f"   Incentive: ${offer.incentive_amount:,.2f} {offer.incentive_type.value}")
        print(f"   Expected ROI: {offer.expected_roi:.0f}%")
        print(f"   Completion Probability: {offer.probability_of_completion:.0%}")
        print(f"   Expected Cost Avoidance: ${offer.expected_cost_avoidance:,.2f}")
        print(f"   Priority Score: {offer.priority_score:.2f}")
        print()