-- VitaNexus Simplified Database Schema for MVP
-- PostgreSQL 15+ without TimescaleDB

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CORE MEMBER MANAGEMENT
-- ============================================================================

CREATE TABLE members (
    member_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_member_id VARCHAR(50) UNIQUE NOT NULL,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')),

    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address_line1 VARCHAR(255),
    city VARCHAR(100),
    state CHAR(2),
    zip_code VARCHAR(10),

    enrollment_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    current_risk_score DECIMAL(5,2) CHECK (current_risk_score BETWEEN 1 AND 100),
    current_risk_category VARCHAR(20) CHECK (current_risk_category IN ('low', 'moderate', 'high', 'critical')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_members_status ON members(status);
CREATE INDEX idx_members_email ON members(email);

-- ============================================================================
-- HEALTH PROFILES
-- ============================================================================

CREATE TABLE member_health_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,

    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    bmi DECIMAL(4,2),

    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    resting_heart_rate INTEGER,

    smoker BOOLEAN DEFAULT FALSE,
    exercise_frequency VARCHAR(50),

    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_health_profiles_member ON member_health_profiles(member_id);

-- ============================================================================
-- HEALTH RISK SCORING
-- ============================================================================

CREATE TABLE health_risk_scores (
    score_id UUID DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    calculation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,

    overall_score DECIMAL(5,2) NOT NULL CHECK (overall_score BETWEEN 1 AND 100),
    risk_category VARCHAR(20) NOT NULL,
    confidence_level DECIMAL(3,2) CHECK (confidence_level BETWEEN 0 AND 1),

    predicted_annual_cost DECIMAL(10,2),
    model_version VARCHAR(20) NOT NULL,

    PRIMARY KEY (member_id, calculation_timestamp)
);

CREATE INDEX idx_risk_scores_member ON health_risk_scores(member_id, calculation_timestamp DESC);

-- ============================================================================
-- WEARABLE DATA
-- ============================================================================

CREATE TABLE wearable_metrics (
    metric_id UUID DEFAULT uuid_generate_v4(),
    member_id UUID NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    recorded_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,

    device_type VARCHAR(50),
    steps INTEGER,
    distance_meters INTEGER,
    active_minutes INTEGER,
    calories_burned INTEGER,

    resting_heart_rate INTEGER,
    sleep_minutes INTEGER,
    sleep_quality_score INTEGER,

    PRIMARY KEY (member_id, recorded_timestamp)
);

CREATE INDEX idx_wearable_member_time ON wearable_metrics(member_id, recorded_timestamp DESC);

-- ============================================================================
-- AUDIT LOGGING (HIPAA Compliance)
-- ============================================================================

CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100) NOT NULL,
    member_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL
);

CREATE INDEX idx_audit_timestamp ON audit_log(event_timestamp DESC);
CREATE INDEX idx_audit_user ON audit_log(user_id, event_timestamp DESC);

-- ============================================================================
-- USERS / AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(50) NOT NULL CHECK (role IN ('member', 'care_manager', 'admin')),
    member_id UUID REFERENCES members(member_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

COMMENT ON DATABASE vitanexus_dev IS 'VitaNexus Health Assurance Cooperative - MVP Schema';