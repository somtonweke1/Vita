"""
Pilot Program Analytics
Validate unit economics and business model assumptions with first 100 members
"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict
import pandas as pd
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class PilotMember:
    """Pilot member data"""
    member_id: str
    enrollment_date: date
    monthly_premium: Decimal
    initial_risk_score: float
    current_risk_score: float
    predicted_annual_cost: Decimal
    actual_costs_ytd: Decimal
    intervention_costs_ytd: Decimal
    programs_enrolled: int
    programs_completed: int
    wearable_connected: bool
    days_active: int  # Days with wearable data


@dataclass
class UnitEconomics:
    """Unit economics metrics for validation"""
    # Acquisition
    member_acquisition_cost: Decimal
    marketing_spend_per_member: Decimal

    # Revenue
    avg_monthly_premium: Decimal
    annual_revenue_per_member: Decimal

    # Costs
    avg_claims_cost: Decimal
    avg_intervention_cost: Decimal
    avg_operating_cost_per_member: Decimal
    total_cost_per_member: Decimal

    # Savings & Profit
    predicted_cost: Decimal
    actual_total_cost: Decimal
    savings_per_member: Decimal
    savings_rate: float  # Percentage

    company_profit_per_member: Decimal
    member_rebate_per_member: Decimal

    # Key Metrics
    ltv_cac_ratio: float  # Lifetime Value / Customer Acquisition Cost
    medical_loss_ratio: float  # Claims / Premium
    intervention_ratio: float  # Interventions / Premium
    profit_margin: float  # Profit / Revenue


@dataclass
class CohortAnalysis:
    """Cohort performance analysis"""
    cohort_name: str  # e.g., "Month 1 Enrollees"
    member_count: int

    avg_risk_score_change: float
    pct_risk_improved: float
    pct_risk_worsened: float

    engagement_rate: float  # % with wearable connected
    program_completion_rate: float

    savings_rate: float
    profit_margin: float


class PilotAnalytics:
    """
    Analytics engine for pilot program.

    Goals:
    1. Validate unit economics (LTV:CAC > 3:1)
    2. Prove savings rate (target: 15-25%)
    3. Measure engagement (target: >70% wearable connection)
    4. Demonstrate health improvement (target: 12-point risk reduction)
    5. Confirm intervention ROI (target: >200%)
    """

    def __init__(self, target_savings_rate: float = 0.20):
        self.target_savings_rate = target_savings_rate
        self.target_ltv_cac = 3.0
        self.target_engagement_rate = 0.70
        self.target_risk_reduction = 12.0

    def calculate_unit_economics(
        self,
        members: List[PilotMember],
        marketing_spend: Decimal,
        operating_expenses: Decimal
    ) -> UnitEconomics:
        """
        Calculate unit economics for pilot cohort.

        This is the CRITICAL calculation that proves the business model works.
        """
        n = len(members)
        if n == 0:
            raise ValueError("Cannot calculate unit economics with zero members")

        # Acquisition costs
        mac = marketing_spend / n
        marketing_per_member = marketing_spend / n

        # Revenue (annualized)
        total_premiums = sum(m.monthly_premium for m in members)
        avg_monthly_premium = total_premiums / n
        annual_revenue = avg_monthly_premium * 12

        # Claims costs (annualized from YTD)
        avg_claims = sum(m.actual_costs_ytd for m in members) / n
        avg_days_enrolled = np.mean([
            (date.today() - m.enrollment_date).days for m in members
        ])
        annualized_claims = avg_claims / avg_days_enrolled * 365 if avg_days_enrolled > 0 else avg_claims

        # Intervention costs (annualized)
        avg_interventions = sum(m.intervention_costs_ytd for m in members) / n
        annualized_interventions = avg_interventions / avg_days_enrolled * 365 if avg_days_enrolled > 0 else avg_interventions

        # Operating costs (annualized)
        avg_operating = operating_expenses / n

        # Total costs
        total_cost = annualized_claims + annualized_interventions + avg_operating

        # Savings calculation
        avg_predicted = sum(m.predicted_annual_cost for m in members) / n
        savings = avg_predicted - annualized_claims - annualized_interventions
        savings_rate = float(savings / avg_predicted) if avg_predicted > 0 else 0.0

        # Profit split (70/30)
        company_profit = savings * Decimal('0.70')
        member_rebate = savings * Decimal('0.30')

        # LTV (3-year horizon, no discounting for simplicity)
        ltv = (annual_revenue - total_cost) * 3
        ltv_cac_ratio = float(ltv / mac) if mac > 0 else 0.0

        # Ratios
        mlr = float(annualized_claims / annual_revenue) if annual_revenue > 0 else 0.0
        intervention_ratio = float(annualized_interventions / annual_revenue) if annual_revenue > 0 else 0.0
        profit_margin = float(company_profit / annual_revenue) if annual_revenue > 0 else 0.0

        return UnitEconomics(
            member_acquisition_cost=mac,
            marketing_spend_per_member=marketing_per_member,
            avg_monthly_premium=avg_monthly_premium,
            annual_revenue_per_member=annual_revenue,
            avg_claims_cost=annualized_claims,
            avg_intervention_cost=annualized_interventions,
            avg_operating_cost_per_member=avg_operating,
            total_cost_per_member=total_cost,
            predicted_cost=avg_predicted,
            actual_total_cost=annualized_claims + annualized_interventions,
            savings_per_member=savings,
            savings_rate=savings_rate,
            company_profit_per_member=company_profit,
            member_rebate_per_member=member_rebate,
            ltv_cac_ratio=ltv_cac_ratio,
            medical_loss_ratio=mlr,
            intervention_ratio=intervention_ratio,
            profit_margin=profit_margin
        )

    def analyze_health_outcomes(self, members: List[PilotMember]) -> Dict:
        """
        Analyze health outcome improvements across pilot cohort.
        """
        risk_changes = [m.current_risk_score - m.initial_risk_score for m in members]
        avg_risk_change = np.mean(risk_changes)

        improved = sum(1 for change in risk_changes if change < -5)  # >5 point improvement
        worsened = sum(1 for change in risk_changes if change > 5)
        stable = len(members) - improved - worsened

        # Engagement metrics
        wearable_connected = sum(1 for m in members if m.wearable_connected)
        engaged_members = sum(1 for m in members if m.days_active >= 20)  # Active 20+ days

        # Program metrics
        enrolled_in_programs = sum(1 for m in members if m.programs_enrolled > 0)
        completed_programs = sum(m.programs_completed for m in members)
        total_enrollments = sum(m.programs_enrolled for m in members)
        completion_rate = completed_programs / total_enrollments if total_enrollments > 0 else 0.0

        return {
            'avg_risk_score_change': avg_risk_change,
            'pct_improved': improved / len(members) * 100,
            'pct_worsened': worsened / len(members) * 100,
            'pct_stable': stable / len(members) * 100,
            'wearable_connection_rate': wearable_connected / len(members) * 100,
            'engagement_rate': engaged_members / len(members) * 100,
            'program_enrollment_rate': enrolled_in_programs / len(members) * 100,
            'program_completion_rate': completion_rate * 100,
            'target_risk_reduction_met': avg_risk_change <= -self.target_risk_reduction
        }

    def cohort_analysis(
        self,
        members: List[PilotMember],
        group_by: str = 'enrollment_month'
    ) -> List[CohortAnalysis]:
        """
        Break down performance by cohort (enrollment month, risk level, etc.)
        """
        # Group members into cohorts
        cohorts = defaultdict(list)

        for member in members:
            if group_by == 'enrollment_month':
                key = member.enrollment_date.strftime('%Y-%m')
            elif group_by == 'initial_risk':
                if member.initial_risk_score <= 30:
                    key = 'Low Risk'
                elif member.initial_risk_score <= 60:
                    key = 'Moderate Risk'
                elif member.initial_risk_score <= 85:
                    key = 'High Risk'
                else:
                    key = 'Critical Risk'
            else:
                key = 'All'

            cohorts[key].append(member)

        # Analyze each cohort
        results = []
        for cohort_name, cohort_members in cohorts.items():
            if len(cohort_members) == 0:
                continue

            # Risk changes
            risk_changes = [m.current_risk_score - m.initial_risk_score for m in cohort_members]
            avg_change = np.mean(risk_changes)
            improved = sum(1 for c in risk_changes if c < -5)
            worsened = sum(1 for c in risk_changes if c > 5)

            # Engagement
            connected = sum(1 for m in cohort_members if m.wearable_connected)
            engagement_rate = connected / len(cohort_members)

            # Programs
            completed = sum(m.programs_completed for m in cohort_members)
            enrolled = sum(m.programs_enrolled for m in cohort_members)
            completion_rate = completed / enrolled if enrolled > 0 else 0.0

            # Financial
            predicted = sum(m.predicted_annual_cost for m in cohort_members)
            actual = sum(m.actual_costs_ytd + m.intervention_costs_ytd for m in cohort_members)
            savings = predicted - actual
            savings_rate = float(savings / predicted) if predicted > 0 else 0.0
            profit_margin = savings_rate * 0.70  # Company share

            results.append(CohortAnalysis(
                cohort_name=cohort_name,
                member_count=len(cohort_members),
                avg_risk_score_change=avg_change,
                pct_risk_improved=improved / len(cohort_members),
                pct_risk_worsened=worsened / len(cohort_members),
                engagement_rate=engagement_rate,
                program_completion_rate=completion_rate,
                savings_rate=savings_rate,
                profit_margin=profit_margin
            ))

        return sorted(results, key=lambda x: x.cohort_name)

    def generate_pilot_report(
        self,
        members: List[PilotMember],
        marketing_spend: Decimal,
        operating_expenses: Decimal
    ) -> str:
        """
        Generate comprehensive pilot program report for stakeholders.
        """
        economics = self.calculate_unit_economics(members, marketing_spend, operating_expenses)
        health_outcomes = self.analyze_health_outcomes(members)
        cohorts = self.cohort_analysis(members, 'initial_risk')

        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║          VitaNexus Pilot Program Report - {datetime.now().strftime('%Y-%m-%d')}           ║
╚══════════════════════════════════════════════════════════════════════╝

PILOT OVERVIEW
──────────────────────────────────────────────────────────────────────
Total Members: {len(members)}
Pilot Duration: {(date.today() - min(m.enrollment_date for m in members)).days} days
Average Enrollment Period: {np.mean([(date.today() - m.enrollment_date).days for m in members]):.0f} days


UNIT ECONOMICS (The Business Model Proof)
──────────────────────────────────────────────────────────────────────
Customer Acquisition Cost (CAC):        ${economics.member_acquisition_cost:,.2f}

Annual Revenue per Member:              ${economics.annual_revenue_per_member:,.2f}
  - Avg Monthly Premium:                ${economics.avg_monthly_premium:,.2f}

Annual Costs per Member:
  - Claims:                             ${economics.avg_claims_cost:,.2f}
  - Interventions:                      ${economics.avg_intervention_cost:,.2f}
  - Operating:                          ${economics.avg_operating_cost_per_member:,.2f}
  - Total:                              ${economics.total_cost_per_member:,.2f}

SAVINGS GENERATION
──────────────────────────────────────────────────────────────────────
Predicted Cost:                         ${economics.predicted_cost:,.2f}
Actual Cost (Claims + Interventions):   ${economics.actual_total_cost:,.2f}
Net Savings:                            ${economics.savings_per_member:,.2f}
Savings Rate:                           {economics.savings_rate:.1%} {'✓' if economics.savings_rate >= self.target_savings_rate else '✗ (Target: 20%)'}

PROFIT DISTRIBUTION
──────────────────────────────────────────────────────────────────────
Company Profit (70%):                   ${economics.company_profit_per_member:,.2f}
Member Rebates (30%):                   ${economics.member_rebate_per_member:,.2f}

KEY METRICS
──────────────────────────────────────────────────────────────────────
LTV:CAC Ratio:                          {economics.ltv_cac_ratio:.2f}x {'✓' if economics.ltv_cac_ratio >= self.target_ltv_cac else '✗ (Target: 3.0x)'}
Medical Loss Ratio:                     {economics.medical_loss_ratio:.1%} (Industry: 85%)
Intervention Ratio:                     {economics.intervention_ratio:.1%}
Profit Margin:                          {economics.profit_margin:.1%}


HEALTH OUTCOMES
──────────────────────────────────────────────────────────────────────
Average Risk Score Change:              {health_outcomes['avg_risk_score_change']:+.1f} points {'✓' if health_outcomes['target_risk_reduction_met'] else '✗ (Target: -12.0)'}
Members Improved:                       {health_outcomes['pct_improved']:.0f}%
Members Worsened:                       {health_outcomes['pct_worsened']:.0f}%
Members Stable:                         {health_outcomes['pct_stable']:.0f}%


ENGAGEMENT METRICS
──────────────────────────────────────────────────────────────────────
Wearable Connection Rate:               {health_outcomes['wearable_connection_rate']:.0f}% {'✓' if health_outcomes['wearable_connection_rate'] >= 70 else '✗ (Target: 70%)'}
Active Engagement Rate:                 {health_outcomes['engagement_rate']:.0f}%
Program Enrollment Rate:                {health_outcomes['program_enrollment_rate']:.0f}%
Program Completion Rate:                {health_outcomes['program_completion_rate']:.0f}%


COHORT ANALYSIS (By Initial Risk Level)
──────────────────────────────────────────────────────────────────────
"""

        for cohort in cohorts:
            report += f"""
{cohort.cohort_name}: {cohort.member_count} members
  Risk Change:         {cohort.avg_risk_score_change:+.1f} pts
  Engagement:          {cohort.engagement_rate:.0%}
  Completion:          {cohort.program_completion_rate:.0%}
  Savings Rate:        {cohort.savings_rate:.1%}
  Profit Margin:       {cohort.profit_margin:.1%}
"""

        report += f"""

VALIDATION STATUS
──────────────────────────────────────────────────────────────────────
✓ = Target Met, ✗ = Target Missed

Business Model Validation:
  [{'✓' if economics.ltv_cac_ratio >= 3.0 else '✗'}] LTV:CAC >= 3.0x
  [{'✓' if economics.savings_rate >= 0.15 else '✗'}] Savings Rate >= 15%
  [{'✓' if economics.profit_margin >= 0.10 else '✗'}] Profit Margin >= 10%

Health Outcomes Validation:
  [{'✓' if health_outcomes['avg_risk_score_change'] <= -12 else '✗'}] Risk Reduction >= 12 points
  [{'✓' if health_outcomes['pct_improved'] >= 60 else '✗'}] >60% Members Improved

Engagement Validation:
  [{'✓' if health_outcomes['wearable_connection_rate'] >= 70 else '✗'}] >70% Wearable Connection
  [{'✓' if health_outcomes['program_completion_rate'] >= 65 else '✗'}] >65% Program Completion


NEXT STEPS
──────────────────────────────────────────────────────────────────────
1. Continue pilot to 100 members for statistical significance
2. Refine intervention selection algorithms based on ROI data
3. Optimize member acquisition channels
4. Prepare for Series A fundraising with validated unit economics
5. Plan multi-state expansion strategy

═══════════════════════════════════════════════════════════════════════
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return report


# Example usage
if __name__ == "__main__":
    # Create sample pilot members
    members = [
        PilotMember(
            member_id=f"M{i:03d}",
            enrollment_date=date.today() - timedelta(days=90),
            monthly_premium=Decimal('450'),
            initial_risk_score=75.0,
            current_risk_score=62.0,
            predicted_annual_cost=Decimal('14000'),
            actual_costs_ytd=Decimal('2800'),
            intervention_costs_ytd=Decimal('200'),
            programs_enrolled=2,
            programs_completed=1,
            wearable_connected=True,
            days_active=75
        )
        for i in range(50)  # 50 members for demo
    ]

    analytics = PilotAnalytics()

    report = analytics.generate_pilot_report(
        members=members,
        marketing_spend=Decimal('10000'),  # $200/member
        operating_expenses=Decimal('30000')  # $600/member/year
    )

    print(report)