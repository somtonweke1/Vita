/**
 * TypeScript types for VitaNexus API
 * Auto-generated from OpenAPI spec
 */

export type RiskCategory = 'low' | 'moderate' | 'high' | 'critical';
export type MemberStatus = 'active' | 'suspended' | 'terminated' | 'pending';
export type Gender = 'M' | 'F' | 'O';

export interface Address {
  line1: string;
  line2?: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
}

export interface Member {
  member_id: string;
  external_member_id?: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  age: number;
  gender: Gender;
  email: string;
  phone?: string;
  address?: Address;
  enrollment_date: string;
  status: MemberStatus;
  current_risk_score?: number;
  current_risk_category?: RiskCategory;
  created_at: string;
  updated_at: string;
}

export interface HealthProfile {
  height_cm?: number;
  weight_kg?: number;
  bmi?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  glucose_level?: number;
  cholesterol_total?: number;
  cholesterol_hdl?: number;
  cholesterol_ldl?: number;
  smoker?: boolean;
  alcohol_use?: string;
  reported_stress_level?: number;
  last_updated?: string;
}

export interface RiskFactor {
  factor_type: string;
  factor_name: string;
  contribution_points: number;
  severity: string;
  description: string;
  recommended_action: string;
}

export interface HealthScore {
  member_id: string;
  score: number;
  risk_category: RiskCategory;
  confidence_level: number;
  predicted_annual_cost: number;
  cost_prediction_range: {
    low: number;
    high: number;
  };
  component_scores: {
    demographic: number;
    clinical: number;
    behavioral: number;
    utilization: number;
  };
  top_risk_factors: RiskFactor[];
  recommended_interventions: string[];
  calculation_timestamp: string;
  model_version: string;
  data_completeness_score: number;
}

export interface WearableMetric {
  recorded_timestamp: string;
  device_type?: string;
  steps?: number;
  distance_meters?: number;
  active_minutes?: number;
  calories_burned?: number;
  resting_heart_rate?: number;
  avg_heart_rate?: number;
  sleep_minutes?: number;
  deep_sleep_minutes?: number;
  rem_sleep_minutes?: number;
  sleep_quality_score?: number;
}

export interface InterventionProgram {
  program_id: string;
  program_name: string;
  program_type: string;
  description: string;
  duration_weeks: number;
  delivery_method: string;
  cost_per_participant: number;
  eligibility_criteria: string[];
  expected_outcomes: {
    risk_reduction: number;
    cost_avoidance: number;
    completion_rate: number;
  };
}

export interface ProgramEnrollment {
  enrollment_id: string;
  member_id: string;
  program_id: string;
  program_name: string;
  enrollment_date: string;
  scheduled_start_date: string;
  enrollment_status: string;
  progress?: {
    sessions_attended: number;
    sessions_total: number;
    attendance_rate: number;
  };
}

export interface Rebate {
  rebate_id: string;
  member_id: string;
  rebate_period: string;
  calculation_date: string;
  base_rebate_amount: number;
  health_improvement_bonus: number;
  participation_bonus: number;
  total_rebate_amount: number;
  distribution_date?: string;
  distribution_status: string;
}

export interface PremiumInfo {
  member_id: string;
  policy_number: string;
  monthly_premium: number;
  annual_deductible: number;
  out_of_pocket_max: number;
  deductible_met_ytd: number;
  out_of_pocket_met_ytd: number;
  next_payment_due: string;
  payment_history: Array<{
    payment_date: string;
    amount: number;
    status: string;
  }>;
}