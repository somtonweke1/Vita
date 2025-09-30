"""
VitaNexus Financial Modeling Engine

Core financial algorithms for risk pool management, savings calculation,
premium optimization, and intervention ROI analysis.

This is the heart of VitaNexus's business model innovation - aligning profitability
with member wellness through sophisticated financial modeling.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np
from statistics import mean, stdev
import logging

logger = logging.getLogger(__name__)


class InterventionType(Enum):
    """Categories of wellness interventions"""
    PREVENTIVE_SCREENING = "preventive_screening"
    CHRONIC_DISEASE_MANAGEMENT = "chronic_disease_management"
    BEHAVIORAL_COACHING = "behavioral_coaching"
    MENTAL_HEALTH = "mental_health"
    NUTRITION_COUNSELING = "nutrition_counseling"
    FITNESS_PROGRAM = "fitness_program"
    SMOKING_CESSATION = "smoking_cessation"
    MEDICATION_ADHERENCE = "medication_adherence"
    CARE_COORDINATION = "care_coordination"


@dataclass
class MemberFinancialProfile:
    """Financial data for a member"""
    member_id: str
    monthly_premium: Decimal
    months_enrolled: int

    # Historical costs
    actual_costs_ytd: Decimal
    predicted_costs_at_enrollment: Decimal

    # Risk metrics
    current_risk_score: float
    enrollment_risk_score: float

    # Interventions
    interventions_received: List[str] = field(default_factory=list)
    intervention_costs_ytd: Decimal = Decimal('0')

    # Engagement
    prevention_program_participation: bool = False
    adherence_score: float = 0.0  # 0-1 scale


@dataclass
class RiskPoolMetrics:
    """Aggregate metrics for the member risk pool"""
    total_members: int
    total_monthly_premiums: Decimal
    total_reserves: Decimal

    # Risk distribution
    low_risk_count: int
    moderate_risk_count: int
    high_risk_count: int
    critical_risk_count: int

    # Costs
    total_claims_ytd: Decimal
    total_intervention_costs_ytd: Decimal
    average_cost_per_member: Decimal

    # Performance
    savings_ytd: Decimal
    savings_percentage: float

    calculation_date: date


@dataclass
class InterventionROI:
    """ROI calculation for a specific intervention"""
    intervention_type: InterventionType
    member_id: str

    # Costs
    intervention_cost: Decimal

    # Expected impact
    risk_score_reduction: float  # Points reduced
    estimated_cost_avoidance: Decimal  # Annual

    # ROI metrics
    roi_percentage: float  # (benefit - cost) / cost
    payback_period_months: float
    net_present_value: Decimal  # 3-year horizon

    # Probability of success
    success_probability: float  # 0-1
    expected_value: Decimal  # NPV * probability

    priority_score: float  # Ranking metric for resource allocation


@dataclass
class FinancialForecast:
    """P&L projection for specified period"""
    forecast_period: str  # e.g., "2024-Q3"

    # Revenue
    projected_premium_revenue: Decimal

    # Expenses
    projected_claims_costs: Decimal
    projected_intervention_costs: Decimal
    projected_operating_expenses: Decimal

    # Outcomes
    projected_total_savings: Decimal
    projected_company_profit: Decimal
    projected_member_rebates: Decimal

    # Ratios
    medical_loss_ratio: float  # Claims / Premium
    intervention_ratio: float  # Interventions / Premium
    profit_margin: float

    # Confidence
    confidence_interval_low: Decimal
    confidence_interval_high: Decimal


class FinancialEngine:
    """
    Core financial modeling engine for VitaNexus.

    Implements the key financial algorithms that enable the business model:
    1. Risk pool management and reserve calculation
    2. Savings measurement (predicted vs actual costs)
    3. Premium adjustment based on outcomes
    4. Intervention ROI optimization
    """

    def __init__(self):
        # Business model parameters
        self.company_profit_share = Decimal('0.70')  # 70% of savings to company
        self.member_rebate_share = Decimal('0.30')  # 30% returned to members

        # Risk reserve parameters
        self.reserve_safety_factor = Decimal('1.35')  # 135% of expected costs
        self.minimum_reserve_months = 3  # Minimum months of expenses in reserve

        # Premium adjustment parameters
        self.max_annual_premium_increase = Decimal('0.15')  # Max 15% increase
        self.max_annual_premium_decrease = Decimal('0.20')  # Max 20% decrease

        # ROI parameters
        self.discount_rate = Decimal('0.08')  # 8% annual discount rate
        self.roi_threshold = 1.5  # Minimum 150% ROI for intervention approval

        # National benchmarks
        self.national_avg_annual_cost = Decimal('5800')
        self.national_medical_loss_ratio = 0.85  # 85% typical in industry

    def calculate_risk_pool_metrics(
        self,
        members: List[MemberFinancialProfile],
        risk_categories: Dict[str, str]  # member_id -> risk_category
    ) -> RiskPoolMetrics:
        """
        Calculate aggregate financial metrics for the risk pool.

        Args:
            members: List of all member financial profiles
            risk_categories: Mapping of member_id to current risk category

        Returns:
            RiskPoolMetrics with comprehensive pool analysis
        """
        logger.info(f"Calculating risk pool metrics for {len(members)} members")

        total_members = len(members)
        total_premiums = sum(m.monthly_premium for m in members)
        total_claims = sum(m.actual_costs_ytd for m in members)
        total_interventions = sum(m.intervention_costs_ytd for m in members)

        # Risk distribution
        risk_dist = {'low': 0, 'moderate': 0, 'high': 0, 'critical': 0}
        for member_id, category in risk_categories.items():
            if category in risk_dist:
                risk_dist[category] += 1

        # Calculate savings
        total_predicted = sum(m.predicted_costs_at_enrollment for m in members)
        actual_spend = total_claims + total_interventions
        savings = total_predicted - actual_spend
        savings_pct = float(savings / total_predicted * 100) if total_predicted > 0 else 0.0

        # Calculate required reserves
        avg_monthly_cost = total_claims / max(sum(m.months_enrolled for m in members), 1)
        required_reserves = avg_monthly_cost * self.minimum_reserve_months * self.reserve_safety_factor

        avg_cost_per_member = total_claims / total_members if total_members > 0 else Decimal('0')

        return RiskPoolMetrics(
            total_members=total_members,
            total_monthly_premiums=total_premiums,
            total_reserves=required_reserves,
            low_risk_count=risk_dist['low'],
            moderate_risk_count=risk_dist['moderate'],
            high_risk_count=risk_dist['high'],
            critical_risk_count=risk_dist['critical'],
            total_claims_ytd=total_claims,
            total_intervention_costs_ytd=total_interventions,
            average_cost_per_member=avg_cost_per_member,
            savings_ytd=savings,
            savings_percentage=savings_pct,
            calculation_date=date.today()
        )

    def calculate_savings_and_distribution(
        self,
        predicted_costs: Decimal,
        actual_claims: Decimal,
        intervention_costs: Decimal
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculate net savings and distribution to company vs members.

        Formula:
            Net Savings = (Predicted Costs) - (Actual Claims + Intervention Costs)
            Company Profit = Net Savings × Company Share (70%)
            Member Rebates = Net Savings × Member Share (30%)

        Returns:
            (total_savings, company_profit, member_rebates)
        """
        total_savings = predicted_costs - actual_claims - intervention_costs

        if total_savings <= 0:
            # No savings to distribute
            return (total_savings, Decimal('0'), Decimal('0'))

        company_profit = (total_savings * self.company_profit_share).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        member_rebates = (total_savings * self.member_rebate_share).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        return (total_savings, company_profit, member_rebates)

    def calculate_member_rebate(
        self,
        member: MemberFinancialProfile,
        total_pool_savings: Decimal,
        total_pool_premiums: Decimal
    ) -> Decimal:
        """
        Calculate individual member's share of savings rebate.

        Rebate is proportional to:
        1. Member's premium contribution (50%)
        2. Member's health improvement (30%)
        3. Member's prevention program participation (20%)

        Args:
            member: Member financial profile
            total_pool_savings: Total savings generated by pool
            total_pool_premiums: Total premiums paid by pool

        Returns:
            Rebate amount for member
        """
        if total_pool_savings <= 0:
            return Decimal('0')

        # Member's portion of total rebate pool
        total_rebate_pool = total_pool_savings * self.member_rebate_share

        # Base share (proportional to premium paid)
        member_total_premium = member.monthly_premium * member.months_enrolled
        base_share = (member_total_premium / total_pool_premiums) * total_rebate_pool * Decimal('0.50')

        # Health improvement bonus
        risk_improvement = member.enrollment_risk_score - member.current_risk_score
        improvement_factor = max(Decimal('0'), Decimal(str(risk_improvement / 100)))
        improvement_bonus = (member_total_premium / total_pool_premiums) * total_rebate_pool * Decimal('0.30') * improvement_factor

        # Participation bonus
        participation_bonus = Decimal('0')
        if member.prevention_program_participation:
            participation_bonus = (member_total_premium / total_pool_premiums) * total_rebate_pool * Decimal('0.20')

        total_rebate = (base_share + improvement_bonus + participation_bonus).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        return total_rebate

    def calculate_premium_adjustment(
        self,
        member: MemberFinancialProfile,
        current_premium: Decimal,
        risk_pool_metrics: RiskPoolMetrics
    ) -> Tuple[Decimal, str]:
        """
        Calculate adjusted premium for member based on risk and pool performance.

        Factors considered:
        1. Change in member's risk score (40%)
        2. Overall pool performance (30%)
        3. Member's individual cost experience (20%)
        4. Regional cost trends (10%)

        Returns:
            (new_premium, adjustment_reason)
        """
        # Factor 1: Risk score change
        risk_change = member.current_risk_score - member.enrollment_risk_score
        risk_adjustment = Decimal(str(risk_change / 100)) * Decimal('0.40')

        # Factor 2: Pool performance
        pool_adjustment = Decimal('0')
        if risk_pool_metrics.savings_percentage < -10:  # Pool losing money
            pool_adjustment = Decimal('0.10') * Decimal('0.30')
        elif risk_pool_metrics.savings_percentage < 0:
            pool_adjustment = Decimal('0.05') * Decimal('0.30')
        elif risk_pool_metrics.savings_percentage > 20:  # Pool doing very well
            pool_adjustment = Decimal('-0.10') * Decimal('0.30')
        elif risk_pool_metrics.savings_percentage > 10:
            pool_adjustment = Decimal('-0.05') * Decimal('0.30')

        # Factor 3: Individual cost experience
        cost_ratio = member.actual_costs_ytd / (member.monthly_premium * member.months_enrolled)
        if cost_ratio > Decimal('1.5'):
            cost_adjustment = Decimal('0.15') * Decimal('0.20')
        elif cost_ratio > Decimal('1.0'):
            cost_adjustment = Decimal('0.08') * Decimal('0.20')
        elif cost_ratio < Decimal('0.5'):
            cost_adjustment = Decimal('-0.15') * Decimal('0.20')
        else:
            cost_adjustment = Decimal('0')

        # Factor 4: Regional trends (simplified - would use actual regional data)
        regional_adjustment = Decimal('0.03') * Decimal('0.10')  # 3% medical inflation

        # Total adjustment
        total_adjustment = risk_adjustment + pool_adjustment + cost_adjustment + regional_adjustment

        # Apply caps
        total_adjustment = max(
            -self.max_annual_premium_decrease,
            min(self.max_annual_premium_increase, total_adjustment)
        )

        new_premium = (current_premium * (Decimal('1') + total_adjustment)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        # Generate explanation
        if total_adjustment > Decimal('0.05'):
            reason = "Premium increased due to higher health risk and/or increased utilization"
        elif total_adjustment < Decimal('-0.05'):
            reason = "Premium reduced due to improved health and excellent pool performance"
        else:
            reason = "Premium adjusted for medical inflation and market conditions"

        return (new_premium, reason)

    def calculate_intervention_roi(
        self,
        member: MemberFinancialProfile,
        intervention_type: InterventionType,
        intervention_cost: Decimal,
        expected_risk_reduction: float,
        expected_adherence: float = 0.7
    ) -> InterventionROI:
        """
        Calculate ROI for a proposed intervention for a specific member.

        Args:
            member: Member financial profile
            intervention_type: Type of intervention
            intervention_cost: Cost to deliver intervention
            expected_risk_reduction: Expected reduction in risk score (points)
            expected_adherence: Probability member will complete program (0-1)

        Returns:
            InterventionROI with comprehensive ROI metrics
        """
        # Estimate cost avoidance from risk reduction
        # Rule of thumb: 1 risk score point = $580 in annual costs
        annual_cost_avoidance = Decimal(str(expected_risk_reduction * 580))

        # Calculate 3-year NPV
        npv = Decimal('0')
        for year in range(1, 4):
            # Diminishing returns over time (80% retention per year)
            year_benefit = annual_cost_avoidance * (Decimal('0.80') ** (year - 1))
            discount_factor = (Decimal('1') + self.discount_rate) ** year
            npv += year_benefit / discount_factor

        npv -= intervention_cost

        # Calculate ROI percentage
        if intervention_cost > 0:
            roi_pct = float((npv / intervention_cost) * 100)
        else:
            roi_pct = 0.0

        # Payback period
        if annual_cost_avoidance > 0:
            payback_months = float((intervention_cost / annual_cost_avoidance) * 12)
        else:
            payback_months = 999.9  # Never pays back

        # Expected value accounting for adherence probability
        expected_value = npv * Decimal(str(expected_adherence))

        # Priority score (higher = more attractive intervention)
        priority_score = float(expected_value / (intervention_cost + Decimal('1'))) * expected_adherence

        return InterventionROI(
            intervention_type=intervention_type,
            member_id=member.member_id,
            intervention_cost=intervention_cost,
            risk_score_reduction=expected_risk_reduction,
            estimated_cost_avoidance=annual_cost_avoidance,
            roi_percentage=roi_pct,
            payback_period_months=payback_months,
            net_present_value=npv.quantize(Decimal('0.01')),
            success_probability=expected_adherence,
            expected_value=expected_value.quantize(Decimal('0.01')),
            priority_score=priority_score
        )

    def optimize_intervention_budget(
        self,
        available_budget: Decimal,
        candidate_interventions: List[InterventionROI]
    ) -> List[InterventionROI]:
        """
        Optimize allocation of intervention budget across candidates.

        Uses greedy algorithm to select interventions with highest expected value
        until budget is exhausted.

        Args:
            available_budget: Total budget available for interventions
            candidate_interventions: All possible interventions to consider

        Returns:
            List of selected interventions that maximize expected value
        """
        # Sort by priority score (expected value per dollar)
        sorted_interventions = sorted(
            candidate_interventions,
            key=lambda x: x.priority_score,
            reverse=True
        )

        selected = []
        remaining_budget = available_budget

        for intervention in sorted_interventions:
            # Only select if:
            # 1. We have budget
            # 2. ROI exceeds threshold
            # 3. Expected value is positive
            if (remaining_budget >= intervention.intervention_cost and
                intervention.roi_percentage >= (self.roi_threshold * 100) and
                intervention.expected_value > 0):

                selected.append(intervention)
                remaining_budget -= intervention.intervention_cost

                logger.info(
                    f"Selected {intervention.intervention_type.value} for member "
                    f"{intervention.member_id}: ROI {intervention.roi_percentage:.1f}%, "
                    f"EV ${intervention.expected_value:,.2f}"
                )

        logger.info(
            f"Optimized intervention portfolio: {len(selected)} interventions, "
            f"${available_budget - remaining_budget:,.2f} allocated, "
            f"${remaining_budget:,.2f} remaining"
        )

        return selected

    def forecast_financial_performance(
        self,
        current_members: List[MemberFinancialProfile],
        risk_pool: RiskPoolMetrics,
        months_forward: int = 3
    ) -> FinancialForecast:
        """
        Generate P&L forecast for specified future period.

        Args:
            current_members: Current member population
            risk_pool: Current risk pool metrics
            months_forward: Number of months to forecast

        Returns:
            FinancialForecast with projected financials
        """
        period_label = f"Next {months_forward} months"

        # Revenue projection
        projected_premiums = risk_pool.total_monthly_premiums * months_forward

        # Claims cost projection (based on historical MLR with trend)
        historical_mlr = float(risk_pool.total_claims_ytd / (
            sum(m.monthly_premium * m.months_enrolled for m in current_members)
        ))
        trend_factor = Decimal('1.03')  # 3% annual medical inflation
        projected_claims = projected_premiums * Decimal(str(historical_mlr)) * trend_factor

        # Intervention costs (typically 5-8% of premium)
        intervention_ratio = Decimal('0.06')
        projected_interventions = projected_premiums * intervention_ratio

        # Operating expenses (15% of premium for MVP stage)
        projected_opex = projected_premiums * Decimal('0.15')

        # Calculate savings and profit
        # Savings = predicted costs - actual costs
        # For forecast, assume 15% savings rate (conservative)
        expected_costs_without_intervention = projected_premiums * Decimal('0.85')
        actual_costs_with_intervention = projected_claims + projected_interventions
        projected_savings = expected_costs_without_intervention - actual_costs_with_intervention

        company_profit = projected_savings * self.company_profit_share - projected_opex
        member_rebates = projected_savings * self.member_rebate_share

        # Calculate ratios
        mlr = float(projected_claims / projected_premiums) if projected_premiums > 0 else 0.85
        intervention_r = float(projected_interventions / projected_premiums) if projected_premiums > 0 else 0.06
        profit_margin = float(company_profit / projected_premiums) if projected_premiums > 0 else 0.0

        # Confidence intervals (Monte Carlo simulation would be used in production)
        volatility = Decimal('0.20')  # 20% volatility
        ci_low = company_profit * (Decimal('1') - volatility)
        ci_high = company_profit * (Decimal('1') + volatility)

        return FinancialForecast(
            forecast_period=period_label,
            projected_premium_revenue=projected_premiums.quantize(Decimal('0.01')),
            projected_claims_costs=projected_claims.quantize(Decimal('0.01')),
            projected_intervention_costs=projected_interventions.quantize(Decimal('0.01')),
            projected_operating_expenses=projected_opex.quantize(Decimal('0.01')),
            projected_total_savings=projected_savings.quantize(Decimal('0.01')),
            projected_company_profit=company_profit.quantize(Decimal('0.01')),
            projected_member_rebates=member_rebates.quantize(Decimal('0.01')),
            medical_loss_ratio=mlr,
            intervention_ratio=intervention_r,
            profit_margin=profit_margin,
            confidence_interval_low=ci_low.quantize(Decimal('0.01')),
            confidence_interval_high=ci_high.quantize(Decimal('0.01'))
        )


# Example usage and testing
if __name__ == "__main__":
    # Create sample member population
    members = [
        MemberFinancialProfile(
            member_id="M001",
            monthly_premium=Decimal('450'),
            months_enrolled=12,
            actual_costs_ytd=Decimal('3200'),
            predicted_costs_at_enrollment=Decimal('5800'),
            current_risk_score=35.0,
            enrollment_risk_score=58.0,
            intervention_costs_ytd=Decimal('250'),
            prevention_program_participation=True,
            adherence_score=0.85
        ),
        MemberFinancialProfile(
            member_id="M002",
            monthly_premium=Decimal('520'),
            months_enrolled=12,
            actual_costs_ytd=Decimal('12500'),
            predicted_costs_at_enrollment=Decimal('14200'),
            current_risk_score=72.0,
            enrollment_risk_score=75.0,
            intervention_costs_ytd=Decimal('800'),
            prevention_program_participation=True,
            adherence_score=0.70
        ),
        MemberFinancialProfile(
            member_id="M003",
            monthly_premium=Decimal('380'),
            months_enrolled=12,
            actual_costs_ytd=Decimal('1800'),
            predicted_costs_at_enrollment=Decimal('2400'),
            current_risk_score=18.0,
            enrollment_risk_score=22.0,
            intervention_costs_ytd=Decimal('120'),
            prevention_program_participation=False,
            adherence_score=0.50
        ),
    ]

    risk_categories = {
        "M001": "moderate",
        "M002": "high",
        "M003": "low"
    }

    # Initialize engine
    engine = FinancialEngine()

    # Calculate risk pool metrics
    pool_metrics = engine.calculate_risk_pool_metrics(members, risk_categories)

    print(f"\n{'='*70}")
    print("RISK POOL FINANCIAL METRICS")
    print(f"{'='*70}")
    print(f"Total Members: {pool_metrics.total_members}")
    print(f"Monthly Premium Revenue: ${pool_metrics.total_monthly_premiums:,.2f}")
    print(f"Required Reserves: ${pool_metrics.total_reserves:,.2f}")
    print(f"\nRisk Distribution:")
    print(f"  Low Risk: {pool_metrics.low_risk_count}")
    print(f"  Moderate Risk: {pool_metrics.moderate_risk_count}")
    print(f"  High Risk: {pool_metrics.high_risk_count}")
    print(f"  Critical Risk: {pool_metrics.critical_risk_count}")
    print(f"\nCosts:")
    print(f"  Total Claims YTD: ${pool_metrics.total_claims_ytd:,.2f}")
    print(f"  Total Interventions YTD: ${pool_metrics.total_intervention_costs_ytd:,.2f}")
    print(f"  Avg Cost per Member: ${pool_metrics.average_cost_per_member:,.2f}")
    print(f"\nPerformance:")
    print(f"  Savings YTD: ${pool_metrics.savings_ytd:,.2f}")
    print(f"  Savings Percentage: {pool_metrics.savings_percentage:.1f}%")

    # Calculate savings distribution
    total_predicted = sum(m.predicted_costs_at_enrollment for m in members)
    total_actual = sum(m.actual_costs_ytd + m.intervention_costs_ytd for m in members)
    savings, profit, rebates = engine.calculate_savings_and_distribution(
        total_predicted, sum(m.actual_costs_ytd for m in members),
        sum(m.intervention_costs_ytd for m in members)
    )

    print(f"\n{'='*70}")
    print("SAVINGS DISTRIBUTION")
    print(f"{'='*70}")
    print(f"Total Savings: ${savings:,.2f}")
    print(f"Company Profit (70%): ${profit:,.2f}")
    print(f"Member Rebates (30%): ${rebates:,.2f}")

    # Calculate individual member rebates
    print(f"\n{'='*70}")
    print("MEMBER REBATES")
    print(f"{'='*70}")
    total_premiums = sum(m.monthly_premium * m.months_enrolled for m in members)
    for member in members:
        rebate = engine.calculate_member_rebate(member, savings, total_premiums)
        print(f"Member {member.member_id}: ${rebate:,.2f}")

    # Calculate intervention ROI
    print(f"\n{'='*70}")
    print("INTERVENTION ROI ANALYSIS")
    print(f"{'='*70}")

    intervention_roi = engine.calculate_intervention_roi(
        members[1],  # High-risk member
        InterventionType.CHRONIC_DISEASE_MANAGEMENT,
        Decimal('600'),
        expected_risk_reduction=15.0,
        expected_adherence=0.75
    )

    print(f"Intervention: {intervention_roi.intervention_type.value}")
    print(f"Member: {intervention_roi.member_id}")
    print(f"Cost: ${intervention_roi.intervention_cost:,.2f}")
    print(f"Expected Risk Reduction: {intervention_roi.risk_score_reduction:.1f} points")
    print(f"Estimated Annual Cost Avoidance: ${intervention_roi.estimated_cost_avoidance:,.2f}")
    print(f"ROI: {intervention_roi.roi_percentage:.1f}%")
    print(f"Payback Period: {intervention_roi.payback_period_months:.1f} months")
    print(f"NPV (3 years): ${intervention_roi.net_present_value:,.2f}")
    print(f"Expected Value: ${intervention_roi.expected_value:,.2f}")
    print(f"Priority Score: {intervention_roi.priority_score:.2f}")

    # Forecast financial performance
    forecast = engine.forecast_financial_performance(members, pool_metrics, months_forward=3)

    print(f"\n{'='*70}")
    print(f"FINANCIAL FORECAST: {forecast.forecast_period}")
    print(f"{'='*70}")
    print(f"Projected Premium Revenue: ${forecast.projected_premium_revenue:,.2f}")
    print(f"Projected Claims: ${forecast.projected_claims_costs:,.2f}")
    print(f"Projected Interventions: ${forecast.projected_intervention_costs:,.2f}")
    print(f"Projected Operating Expenses: ${forecast.projected_operating_expenses:,.2f}")
    print(f"\nProjected Savings: ${forecast.projected_total_savings:,.2f}")
    print(f"Projected Company Profit: ${forecast.projected_company_profit:,.2f}")
    print(f"Projected Member Rebates: ${forecast.projected_member_rebates:,.2f}")
    print(f"\nKey Ratios:")
    print(f"  Medical Loss Ratio: {forecast.medical_loss_ratio:.1%}")
    print(f"  Intervention Ratio: {forecast.intervention_ratio:.1%}")
    print(f"  Profit Margin: {forecast.profit_margin:.1%}")
    print(f"\nProfit Range (90% CI): ${forecast.confidence_interval_low:,.2f} - ${forecast.confidence_interval_high:,.2f}")
    print(f"{'='*70}\n")