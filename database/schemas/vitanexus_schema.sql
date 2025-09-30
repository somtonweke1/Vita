-- VitaNexus Database Schema
-- PostgreSQL 15+ with TimescaleDB extension for time-series data
-- HIPAA-compliant schema with audit logging and encryption support

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
-- TimescaleDB optional - uncomment if installed
-- CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- ============================================================================
-- CORE MEMBER MANAGEMENT
-- ============================================================================

-- Members table: Core demographic and enrollment information
CREATE TABLE members (
    member_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_member_id VARCHAR(50) UNIQUE NOT NULL, -- For third-party integrations

    -- Personal Information (PHI - encrypted at rest)
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')),

    -- Contact Information
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state CHAR(2),
    zip_code VARCHAR(10),
    country VARCHAR(3) DEFAULT 'USA',

    -- Enrollment
    enrollment_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'suspended', 'terminated', 'pending')),
    termination_date DATE,
    termination_reason TEXT,

    -- Risk Profile
    current_risk_score DECIMAL(5,2) CHECK (current_risk_score BETWEEN 1 AND 100),
    current_risk_category VARCHAR(20) CHECK (current_risk_category IN ('low', 'moderate', 'high', 'critical')),
    enrollment_risk_score DECIMAL(5,2),
    last_risk_calculation_date TIMESTAMP WITH TIME ZONE,

    -- Care Coordination
    has_primary_care_physician BOOLEAN DEFAULT FALSE,
    primary_care_physician_id UUID REFERENCES providers(provider_id),
    assigned_care_manager_id UUID REFERENCES care_managers(care_manager_id),

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

CREATE INDEX idx_members_status ON members(status);
CREATE INDEX idx_members_risk_category ON members(current_risk_category);
CREATE INDEX idx_members_enrollment_date ON members(enrollment_date);
CREATE INDEX idx_members_email ON members(email);


-- Member Health Profiles: Clinical and biometric data
CREATE TABLE member_health_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,

    -- Biometric Data (most recent values)
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    bmi DECIMAL(4,2),
    blood_type VARCHAR(5),

    -- Vital Signs (most recent)
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    resting_heart_rate INTEGER,

    -- Lab Results (most recent)
    glucose_level INTEGER, -- mg/dL
    cholesterol_total INTEGER, -- mg/dL
    cholesterol_hdl INTEGER,
    cholesterol_ldl INTEGER,
    cholesterol_triglycerides INTEGER,
    hba1c DECIMAL(3,1), -- Diabetes marker

    -- Health Behaviors
    smoker BOOLEAN DEFAULT FALSE,
    smoking_pack_years DECIMAL(5,1),
    smoking_quit_date DATE,
    alcohol_use VARCHAR(20) CHECK (alcohol_use IN ('none', 'moderate', 'heavy')),
    exercise_frequency VARCHAR(50),
    diet_quality_score INTEGER CHECK (diet_quality_score BETWEEN 1 AND 10),

    -- Mental Health
    reported_stress_level INTEGER CHECK (reported_stress_level BETWEEN 1 AND 10),
    phq9_depression_score INTEGER CHECK (phq9_depression_score BETWEEN 0 AND 27),
    gad7_anxiety_score INTEGER CHECK (gad7_anxiety_score BETWEEN 0 AND 21),

    -- Social Determinants of Health
    health_literacy_score INTEGER CHECK (health_literacy_score BETWEEN 1 AND 100),
    food_insecurity BOOLEAN DEFAULT FALSE,
    housing_insecurity BOOLEAN DEFAULT FALSE,
    transportation_barriers BOOLEAN DEFAULT FALSE,
    social_isolation_risk BOOLEAN DEFAULT FALSE,

    -- Pregnancy Status (if applicable)
    currently_pregnant BOOLEAN DEFAULT FALSE,
    estimated_delivery_date DATE,

    -- Audit
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(50) -- 'self_reported', 'wearable', 'ehr', 'lab'
);

CREATE UNIQUE INDEX idx_health_profiles_member ON member_health_profiles(member_id);


-- Chronic Conditions: ICD-10 coded diagnoses
CREATE TABLE member_chronic_conditions (
    condition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,

    icd10_code VARCHAR(10) NOT NULL,
    condition_name VARCHAR(255) NOT NULL,
    diagnosis_date DATE,
    resolved_date DATE,
    severity VARCHAR(20) CHECK (severity IN ('mild', 'moderate', 'severe')),

    -- HCC (Hierarchical Condition Category) mapping for risk adjustment
    hcc_code VARCHAR(10),
    hcc_weight DECIMAL(5,3),

    is_active BOOLEAN DEFAULT TRUE,

    -- Source
    diagnosed_by_provider_id UUID REFERENCES providers(provider_id),
    data_source VARCHAR(50),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conditions_member ON member_chronic_conditions(member_id);
CREATE INDEX idx_conditions_active ON member_chronic_conditions(member_id, is_active);
CREATE INDEX idx_conditions_icd10 ON member_chronic_conditions(icd10_code);


-- Medications: Current and historical medication list
CREATE TABLE member_medications (
    medication_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,

    drug_name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    ndc_code VARCHAR(20), -- National Drug Code

    dosage VARCHAR(100),
    frequency VARCHAR(100),
    route VARCHAR(50), -- 'oral', 'injection', 'topical', etc.

    prescribed_date DATE,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Prescriber
    prescribing_provider_id UUID REFERENCES providers(provider_id),

    -- Adherence Tracking
    adherence_score DECIMAL(3,2) CHECK (adherence_score BETWEEN 0 AND 1), -- 0-1 scale
    last_filled_date DATE,
    next_refill_due_date DATE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medications_member_active ON member_medications(member_id, is_active);
CREATE INDEX idx_medications_refill_due ON member_medications(next_refill_due_date)
    WHERE is_active = TRUE;


-- Allergies and Adverse Reactions
CREATE TABLE member_allergies (
    allergy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,

    allergen_type VARCHAR(50) NOT NULL CHECK (allergen_type IN ('drug', 'food', 'environmental')),
    allergen_name VARCHAR(255) NOT NULL,

    reaction_severity VARCHAR(20) CHECK (reaction_severity IN ('mild', 'moderate', 'severe', 'life_threatening')),
    reaction_description TEXT,

    onset_date DATE,
    verified_by_provider_id UUID REFERENCES providers(provider_id),

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_allergies_member ON member_allergies(member_id, is_active);


-- ============================================================================
-- FINANCIAL MANAGEMENT
-- ============================================================================

-- Member Policies: Premium and coverage information
CREATE TABLE member_policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,

    policy_number VARCHAR(50) UNIQUE NOT NULL,
    plan_type VARCHAR(50) NOT NULL, -- 'individual', 'family', 'group'

    -- Premium Information
    monthly_premium DECIMAL(10,2) NOT NULL,
    annual_deductible DECIMAL(10,2),
    out_of_pocket_max DECIMAL(10,2),

    -- Coverage Dates
    effective_date DATE NOT NULL,
    termination_date DATE,

    -- Financial Tracking
    total_premiums_paid_ytd DECIMAL(12,2) DEFAULT 0.00,
    total_claims_paid_ytd DECIMAL(12,2) DEFAULT 0.00,
    deductible_met_ytd DECIMAL(10,2) DEFAULT 0.00,
    out_of_pocket_met_ytd DECIMAL(10,2) DEFAULT 0.00,

    -- Risk Pool Assignment
    risk_pool_id VARCHAR(50), -- Geographic or demographic cohort

    status VARCHAR(20) NOT NULL DEFAULT 'active',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policies_member ON member_policies(member_id);
CREATE INDEX idx_policies_status ON member_policies(status);
CREATE INDEX idx_policies_effective_date ON member_policies(effective_date);


-- Premium Payments
CREATE TABLE premium_payments (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    policy_id UUID NOT NULL REFERENCES member_policies(policy_id) ON DELETE CASCADE,

    payment_amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_period_start DATE NOT NULL,
    payment_period_end DATE NOT NULL,

    payment_method VARCHAR(50), -- 'credit_card', 'bank_transfer', 'check'
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')),

    transaction_id VARCHAR(100),
    payment_processor VARCHAR(50),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_member ON premium_payments(member_id);
CREATE INDEX idx_payments_date ON premium_payments(payment_date);
CREATE INDEX idx_payments_status ON premium_payments(payment_status);


-- Claims: Healthcare utilization and costs
CREATE TABLE claims (
    claim_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    policy_id UUID NOT NULL REFERENCES member_policies(policy_id),

    claim_number VARCHAR(50) UNIQUE NOT NULL,
    claim_type VARCHAR(50) NOT NULL CHECK (claim_type IN ('medical', 'pharmacy', 'dental', 'vision', 'mental_health')),

    -- Service Information
    service_date DATE NOT NULL,
    service_end_date DATE,
    provider_id UUID REFERENCES providers(provider_id),
    facility_name VARCHAR(255),

    -- Coding
    primary_diagnosis_code VARCHAR(10), -- ICD-10
    procedure_codes TEXT[], -- Array of CPT codes
    place_of_service VARCHAR(50), -- 'office', 'hospital_inpatient', 'emergency', 'telemedicine'

    -- Financial
    billed_amount DECIMAL(10,2) NOT NULL,
    allowed_amount DECIMAL(10,2),
    paid_amount DECIMAL(10,2),
    member_responsibility DECIMAL(10,2),
    deductible_applied DECIMAL(10,2) DEFAULT 0.00,
    copay_amount DECIMAL(10,2) DEFAULT 0.00,
    coinsurance_amount DECIMAL(10,2) DEFAULT 0.00,

    -- Processing
    claim_status VARCHAR(20) NOT NULL DEFAULT 'submitted'
        CHECK (claim_status IN ('submitted', 'processing', 'approved', 'denied', 'appealed')),
    submission_date DATE NOT NULL,
    processed_date DATE,
    paid_date DATE,
    denial_reason TEXT,

    -- Fraud Detection
    fraud_risk_score DECIMAL(3,2) CHECK (fraud_risk_score BETWEEN 0 AND 1),
    flagged_for_review BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_claims_member ON claims(member_id);
CREATE INDEX idx_claims_service_date ON claims(service_date);
CREATE INDEX idx_claims_status ON claims(claim_status);
CREATE INDEX idx_claims_provider ON claims(provider_id);
CREATE INDEX idx_claims_fraud_flagged ON claims(flagged_for_review) WHERE flagged_for_review = TRUE;


-- Member Rebates: Savings distribution to members
CREATE TABLE member_rebates (
    rebate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    policy_id UUID NOT NULL REFERENCES member_policies(policy_id),

    rebate_period VARCHAR(50) NOT NULL, -- 'Q1-2024', 'Annual-2024'
    calculation_date DATE NOT NULL,

    -- Calculation Components
    base_rebate_amount DECIMAL(10,2) NOT NULL,
    health_improvement_bonus DECIMAL(10,2) DEFAULT 0.00,
    participation_bonus DECIMAL(10,2) DEFAULT 0.00,
    total_rebate_amount DECIMAL(10,2) NOT NULL,

    -- Distribution
    rebate_method VARCHAR(50), -- 'premium_credit', 'check', 'bank_transfer', 'hsa_contribution'
    distribution_date DATE,
    distribution_status VARCHAR(20) DEFAULT 'pending'
        CHECK (distribution_status IN ('pending', 'processed', 'completed', 'failed')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rebates_member ON member_rebates(member_id);
CREATE INDEX idx_rebates_period ON member_rebates(rebate_period);


-- ============================================================================
-- HEALTH SCORING & ANALYTICS
-- ============================================================================

-- Health Risk Scores (Time-series: TimescaleDB hypertable)
CREATE TABLE health_risk_scores (
    score_id UUID DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    calculation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Overall Score
    overall_score DECIMAL(5,2) NOT NULL CHECK (overall_score BETWEEN 1 AND 100),
    risk_category VARCHAR(20) NOT NULL,
    confidence_level DECIMAL(3,2) CHECK (confidence_level BETWEEN 0 AND 1),

    -- Component Scores
    demographic_score DECIMAL(5,2),
    clinical_score DECIMAL(5,2),
    behavioral_score DECIMAL(5,2),
    utilization_score DECIMAL(5,2),

    -- Cost Prediction
    predicted_annual_cost DECIMAL(10,2),
    predicted_cost_lower_bound DECIMAL(10,2),
    predicted_cost_upper_bound DECIMAL(10,2),

    -- Model Metadata
    model_version VARCHAR(20) NOT NULL,
    data_completeness_score DECIMAL(3,2),
    input_data_hash VARCHAR(64), -- SHA-256 for audit

    PRIMARY KEY (member_id, calculation_timestamp)
);

-- Convert to TimescaleDB hypertable for efficient time-series queries (optional)
-- Uncomment if TimescaleDB is installed:
-- SELECT create_hypertable('health_risk_scores', 'calculation_timestamp',
--     chunk_time_interval => INTERVAL '1 month');

CREATE INDEX idx_risk_scores_member ON health_risk_scores(member_id, calculation_timestamp DESC);
CREATE INDEX idx_risk_scores_category ON health_risk_scores(risk_category, calculation_timestamp DESC);


-- Risk Factors: Detailed breakdown of what contributes to risk score
CREATE TABLE member_risk_factors (
    risk_factor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    score_calculation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,

    factor_type VARCHAR(50) NOT NULL, -- 'chronic_disease', 'behavioral', 'biometric', etc.
    factor_name VARCHAR(255) NOT NULL,
    contribution_points DECIMAL(5,2) NOT NULL,
    severity VARCHAR(20),

    description TEXT,
    recommended_action TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (member_id, score_calculation_timestamp)
        REFERENCES health_risk_scores(member_id, calculation_timestamp) ON DELETE CASCADE
);

CREATE INDEX idx_risk_factors_member_time ON member_risk_factors(member_id, score_calculation_timestamp);


-- ============================================================================
-- WEARABLE & BIOMETRIC TIME-SERIES DATA
-- ============================================================================

-- Wearable Metrics (TimescaleDB hypertable for high-volume streaming data)
CREATE TABLE wearable_metrics (
    metric_id UUID DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    recorded_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Device Information
    device_type VARCHAR(50), -- 'fitbit', 'apple_watch', 'garmin', etc.
    device_id VARCHAR(100),

    -- Activity Metrics
    steps INTEGER,
    distance_meters INTEGER,
    active_minutes INTEGER,
    calories_burned INTEGER,
    floors_climbed INTEGER,

    -- Heart Rate
    resting_heart_rate INTEGER,
    max_heart_rate INTEGER,
    avg_heart_rate INTEGER,
    heart_rate_variability INTEGER, -- HRV in milliseconds

    -- Sleep
    sleep_minutes INTEGER,
    deep_sleep_minutes INTEGER,
    rem_sleep_minutes INTEGER,
    light_sleep_minutes INTEGER,
    awake_minutes INTEGER,
    sleep_quality_score INTEGER CHECK (sleep_quality_score BETWEEN 0 AND 100),

    -- Blood Oxygen
    spo2_percentage DECIMAL(4,2) CHECK (spo2_percentage BETWEEN 0 AND 100),

    -- Stress (if available)
    stress_level INTEGER CHECK (stress_level BETWEEN 0 AND 100),

    -- Data Quality
    data_quality VARCHAR(20) CHECK (data_quality IN ('high', 'medium', 'low')),

    PRIMARY KEY (member_id, recorded_timestamp)
);

-- SELECT create_hypertable('wearable_metrics', 'recorded_timestamp',
--     chunk_time_interval => INTERVAL '7 days');

CREATE INDEX idx_wearable_member_time ON wearable_metrics(member_id, recorded_timestamp DESC);


-- ============================================================================
-- INTERVENTIONS & PREVENTION PROGRAMS
-- ============================================================================

-- Prevention Programs: Available wellness interventions
CREATE TABLE prevention_programs (
    program_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    program_name VARCHAR(255) NOT NULL,
    program_type VARCHAR(50) NOT NULL, -- Maps to InterventionType enum
    description TEXT,

    -- Eligibility Criteria
    target_risk_categories TEXT[], -- ['moderate', 'high']
    target_conditions TEXT[], -- ICD-10 codes or condition names

    -- Program Details
    duration_weeks INTEGER,
    delivery_method VARCHAR(50), -- 'in_person', 'virtual', 'hybrid', 'self_paced'
    cost_per_participant DECIMAL(10,2),

    -- Expected Outcomes
    expected_risk_reduction DECIMAL(5,2), -- Average points
    expected_cost_avoidance_annual DECIMAL(10,2),
    historical_completion_rate DECIMAL(3,2), -- 0-1

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_programs_active ON prevention_programs(is_active);


-- Member Program Enrollments
CREATE TABLE member_program_enrollments (
    enrollment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    program_id UUID NOT NULL REFERENCES prevention_programs(program_id),

    enrollment_date DATE NOT NULL,
    scheduled_start_date DATE,
    actual_start_date DATE,
    scheduled_end_date DATE,
    actual_completion_date DATE,

    enrollment_status VARCHAR(20) NOT NULL DEFAULT 'enrolled'
        CHECK (enrollment_status IN ('enrolled', 'active', 'completed', 'dropped', 'failed')),

    -- Engagement Tracking
    sessions_attended INTEGER DEFAULT 0,
    sessions_total INTEGER,
    attendance_rate DECIMAL(3,2),

    -- Outcomes
    pre_enrollment_risk_score DECIMAL(5,2),
    post_completion_risk_score DECIMAL(5,2),
    risk_score_change DECIMAL(5,2),

    -- Cost
    program_cost_paid DECIMAL(10,2),

    -- ROI Tracking (calculated post-completion)
    actual_cost_avoidance_12mo DECIMAL(10,2),
    roi_percentage DECIMAL(5,2),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_enrollments_member ON member_program_enrollments(member_id);
CREATE INDEX idx_enrollments_program ON member_program_enrollments(program_id);
CREATE INDEX idx_enrollments_status ON member_program_enrollments(enrollment_status);


-- Intervention Recommendations: AI-generated suggestions
CREATE TABLE intervention_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,

    recommended_date DATE NOT NULL,
    recommendation_type VARCHAR(50) NOT NULL,

    program_id UUID REFERENCES prevention_programs(program_id),
    priority_score DECIMAL(5,2), -- Higher = more urgent/valuable
    expected_roi_percentage DECIMAL(5,2),

    recommendation_reason TEXT,

    -- Status
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'presented', 'accepted', 'declined', 'expired')),
    member_response_date DATE,
    member_response_reason TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recommendations_member_status ON intervention_recommendations(member_id, status);
CREATE INDEX idx_recommendations_pending ON intervention_recommendations(recommended_date)
    WHERE status = 'pending';


-- ============================================================================
-- PROVIDER NETWORK
-- ============================================================================

-- Providers: Doctors, specialists, facilities
CREATE TABLE providers (
    provider_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    npi VARCHAR(10) UNIQUE NOT NULL, -- National Provider Identifier

    provider_type VARCHAR(50) NOT NULL, -- 'primary_care', 'specialist', 'hospital', 'lab'
    specialty VARCHAR(100),

    -- Name
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    organization_name VARCHAR(255),

    -- Contact
    phone VARCHAR(20),
    email VARCHAR(255),

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state CHAR(2),
    zip_code VARCHAR(10),

    -- Network Status
    in_network BOOLEAN DEFAULT TRUE,
    network_tier VARCHAR(20), -- 'preferred', 'standard', 'out_of_network'
    contract_effective_date DATE,
    contract_termination_date DATE,

    -- Quality Metrics
    quality_score DECIMAL(3,2) CHECK (quality_score BETWEEN 0 AND 1),
    member_satisfaction_score DECIMAL(3,2),
    readmission_rate DECIMAL(3,2),
    cost_efficiency_score DECIMAL(3,2),

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_providers_npi ON providers(npi);
CREATE INDEX idx_providers_network ON providers(in_network, is_active);
CREATE INDEX idx_providers_specialty ON providers(specialty);


-- Care Managers: Internal staff for high-risk member support
CREATE TABLE care_managers (
    care_manager_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,

    role VARCHAR(50) NOT NULL, -- 'nurse', 'social_worker', 'health_coach'
    credentials VARCHAR(100), -- 'RN', 'LCSW', 'CHES'

    max_caseload INTEGER DEFAULT 50,
    current_caseload INTEGER DEFAULT 0,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Care Coordination Notes
CREATE TABLE care_coordination_notes (
    note_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    care_manager_id UUID NOT NULL REFERENCES care_managers(care_manager_id),

    note_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note_type VARCHAR(50), -- 'assessment', 'intervention', 'follow_up', 'phone_call'

    note_text TEXT NOT NULL,

    -- Action Items
    action_required BOOLEAN DEFAULT FALSE,
    action_due_date DATE,
    action_completed BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_care_notes_member ON care_coordination_notes(member_id, note_date DESC);
CREATE INDEX idx_care_notes_action_required ON care_coordination_notes(care_manager_id, action_due_date)
    WHERE action_required = TRUE AND action_completed = FALSE;


-- ============================================================================
-- AUDIT & COMPLIANCE
-- ============================================================================

-- Audit Log: HIPAA-required access logging
CREATE TABLE audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) NOT NULL, -- 'access', 'modify', 'delete', 'export'

    -- Who
    user_id VARCHAR(100) NOT NULL,
    user_role VARCHAR(50),
    ip_address INET,

    -- What
    table_name VARCHAR(100),
    record_id UUID,
    member_id UUID, -- If PHI was accessed

    -- Details
    action_description TEXT,
    old_values JSONB,
    new_values JSONB,

    -- Result
    success BOOLEAN NOT NULL,
    failure_reason TEXT
);

-- Convert to TimescaleDB hypertable for efficient long-term storage (optional)
-- SELECT create_hypertable('audit_log', 'event_timestamp',
--     chunk_time_interval => INTERVAL '1 month');

CREATE INDEX idx_audit_timestamp ON audit_log(event_timestamp DESC);
CREATE INDEX idx_audit_user ON audit_log(user_id, event_timestamp DESC);
CREATE INDEX idx_audit_member ON audit_log(member_id, event_timestamp DESC)
    WHERE member_id IS NOT NULL;
CREATE INDEX idx_audit_failure ON audit_log(event_timestamp DESC)
    WHERE success = FALSE;


-- Data Access Consent: Member consent tracking for HIPAA
CREATE TABLE member_consent (
    consent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,

    consent_type VARCHAR(50) NOT NULL, -- 'data_sharing', 'research', 'marketing'
    consent_given BOOLEAN NOT NULL,
    consent_date DATE NOT NULL,

    consent_text TEXT, -- Full text of what member consented to
    consent_version VARCHAR(20),

    revoked BOOLEAN DEFAULT FALSE,
    revocation_date DATE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_consent_member ON member_consent(member_id, consent_type);


-- ============================================================================
-- SYSTEM CONFIGURATION
-- ============================================================================

-- Financial Model Parameters: Configurable business rules
CREATE TABLE financial_parameters (
    parameter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    parameter_name VARCHAR(100) UNIQUE NOT NULL,
    parameter_value DECIMAL(10,4) NOT NULL,
    parameter_description TEXT,

    effective_date DATE NOT NULL,
    expiration_date DATE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- Insert default parameters
INSERT INTO financial_parameters (parameter_name, parameter_value, parameter_description, effective_date) VALUES
('company_profit_share', 0.70, 'Percentage of savings retained by company', CURRENT_DATE),
('member_rebate_share', 0.30, 'Percentage of savings returned to members', CURRENT_DATE),
('reserve_safety_factor', 1.35, 'Multiplier for risk reserve calculation', CURRENT_DATE),
('minimum_reserve_months', 3.00, 'Minimum months of expenses in reserve', CURRENT_DATE),
('discount_rate', 0.08, 'Annual discount rate for NPV calculations', CURRENT_DATE),
('intervention_roi_threshold', 1.50, 'Minimum ROI for intervention approval', CURRENT_DATE);


-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active Member Summary View
CREATE VIEW vw_active_members_summary AS
SELECT
    m.member_id,
    m.external_member_id,
    m.first_name,
    m.last_name,
    m.email,
    m.date_of_birth,
    DATE_PART('year', AGE(m.date_of_birth)) AS age,
    m.enrollment_date,
    m.current_risk_score,
    m.current_risk_category,
    mp.monthly_premium,
    mp.total_claims_paid_ytd,
    mp.policy_number,
    COALESCE(recent_score.predicted_annual_cost, 0) AS predicted_annual_cost
FROM members m
JOIN member_policies mp ON m.member_id = mp.member_id AND mp.status = 'active'
LEFT JOIN LATERAL (
    SELECT predicted_annual_cost
    FROM health_risk_scores hrs
    WHERE hrs.member_id = m.member_id
    ORDER BY hrs.calculation_timestamp DESC
    LIMIT 1
) recent_score ON TRUE
WHERE m.status = 'active';


-- Member Financial Performance View
CREATE VIEW vw_member_financial_performance AS
SELECT
    m.member_id,
    mp.policy_id,
    mp.monthly_premium * DATE_PART('month', AGE(CURRENT_DATE, mp.effective_date)) AS total_premiums_paid,
    COALESCE(SUM(c.paid_amount), 0) AS total_claims_paid,
    COALESCE(SUM(mpe.program_cost_paid), 0) AS total_intervention_costs,
    hrs.predicted_annual_cost,
    (hrs.predicted_annual_cost - COALESCE(SUM(c.paid_amount), 0) - COALESCE(SUM(mpe.program_cost_paid), 0)) AS net_savings,
    ((hrs.predicted_annual_cost - COALESCE(SUM(c.paid_amount), 0) - COALESCE(SUM(mpe.program_cost_paid), 0)) /
        NULLIF(hrs.predicted_annual_cost, 0) * 100) AS savings_percentage
FROM members m
JOIN member_policies mp ON m.member_id = mp.member_id
LEFT JOIN claims c ON m.member_id = c.member_id AND c.claim_status = 'approved'
LEFT JOIN member_program_enrollments mpe ON m.member_id = mpe.member_id
LEFT JOIN LATERAL (
    SELECT predicted_annual_cost
    FROM health_risk_scores
    WHERE member_id = m.member_id
    ORDER BY calculation_timestamp DESC
    LIMIT 1
) hrs ON TRUE
WHERE m.status = 'active' AND mp.status = 'active'
GROUP BY m.member_id, mp.policy_id, mp.monthly_premium, mp.effective_date, hrs.predicted_annual_cost;


-- High-Risk Members Requiring Intervention View
CREATE VIEW vw_high_risk_members_needing_intervention AS
SELECT
    m.member_id,
    m.first_name || ' ' || m.last_name AS member_name,
    m.current_risk_score,
    m.current_risk_category,
    m.assigned_care_manager_id,
    cm.first_name || ' ' || cm.last_name AS care_manager_name,
    COUNT(DISTINCT mcc.condition_id) AS chronic_condition_count,
    COALESCE(active_programs.program_count, 0) AS active_program_count,
    m.last_risk_calculation_date
FROM members m
LEFT JOIN care_managers cm ON m.assigned_care_manager_id = cm.care_manager_id
LEFT JOIN member_chronic_conditions mcc ON m.member_id = mcc.member_id AND mcc.is_active = TRUE
LEFT JOIN (
    SELECT member_id, COUNT(*) AS program_count
    FROM member_program_enrollments
    WHERE enrollment_status IN ('enrolled', 'active')
    GROUP BY member_id
) active_programs ON m.member_id = active_programs.member_id
WHERE m.status = 'active'
  AND m.current_risk_category IN ('high', 'critical')
  AND COALESCE(active_programs.program_count, 0) = 0  -- Not in any program
GROUP BY m.member_id, m.first_name, m.last_name, m.current_risk_score, m.current_risk_category,
         m.assigned_care_manager_id, cm.first_name, cm.last_name, active_programs.program_count,
         m.last_risk_calculation_date
ORDER BY m.current_risk_score DESC;


-- ============================================================================
-- TRIGGERS FOR AUTOMATED UPDATES
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to relevant tables
CREATE TRIGGER update_members_updated_at BEFORE UPDATE ON members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON member_policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_claims_updated_at BEFORE UPDATE ON claims
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON prevention_programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Auto-update current_risk_score in members table when new score is calculated
CREATE OR REPLACE FUNCTION update_member_current_risk_score()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE members
    SET
        current_risk_score = NEW.overall_score,
        current_risk_category = NEW.risk_category,
        last_risk_calculation_date = NEW.calculation_timestamp
    WHERE member_id = NEW.member_id;

    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_member_risk_score AFTER INSERT ON health_risk_scores
    FOR EACH ROW EXECUTE FUNCTION update_member_current_risk_score();


-- ============================================================================
-- DATA RETENTION POLICIES
-- ============================================================================

-- TimescaleDB retention policy: Keep wearable data for 2 years
SELECT add_retention_policy('wearable_metrics', INTERVAL '2 years');

-- Keep audit logs for 7 years (HIPAA requirement)
SELECT add_retention_policy('audit_log', INTERVAL '7 years');


-- ============================================================================
-- SECURITY: Row-Level Security (RLS) Examples
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE members ENABLE ROW LEVEL SECURITY;
ALTER TABLE member_health_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;

-- Example policy: Members can only see their own data
CREATE POLICY member_self_access ON members
    FOR SELECT
    USING (member_id = current_setting('app.current_member_id')::UUID);

-- Example policy: Care managers can see their assigned members
CREATE POLICY care_manager_access ON members
    FOR SELECT
    USING (assigned_care_manager_id = current_setting('app.current_care_manager_id')::UUID);

-- Note: In production, implement comprehensive RLS policies for all tables


-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE members IS 'Core member demographic and enrollment information. PHI - encrypted at rest.';
COMMENT ON TABLE health_risk_scores IS 'Time-series health risk scores calculated by ML models. Hypertable for efficient querying.';
COMMENT ON TABLE claims IS 'Healthcare utilization claims. Core data for cost tracking and savings calculation.';
COMMENT ON TABLE member_rebates IS 'Savings distribution to members based on health outcomes and pool performance.';
COMMENT ON TABLE prevention_programs IS 'Wellness intervention programs designed to reduce health risks and costs.';
COMMENT ON TABLE audit_log IS 'HIPAA-compliant audit trail of all PHI access. 7-year retention required.';