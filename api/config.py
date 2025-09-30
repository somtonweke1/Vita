"""
Application Configuration
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "VitaNexus"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/v1"
    cors_origins: List[str] = ["http://localhost:3000"]

    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Encryption
    phi_encryption_key: str

    # OAuth
    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""
    auth0_audience: str = ""

    # Wearables
    fitbit_client_id: str = ""
    fitbit_client_secret: str = ""
    fitbit_redirect_uri: str = ""

    apple_health_team_id: str = ""
    apple_health_key_id: str = ""
    apple_health_private_key_path: str = ""

    garmin_consumer_key: str = ""
    garmin_consumer_secret: str = ""

    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_kms_key_id: str = ""

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@vitanexus.com"

    # Monitoring
    datadog_api_key: str = ""
    datadog_app_key: str = ""
    datadog_enabled: bool = False

    # Rate Limiting
    rate_limit_per_minute: int = 1000

    # Feature Flags
    enable_wearable_sync: bool = True
    enable_real_time_scoring: bool = True

    # Financial Model Parameters
    company_profit_share: float = 0.70
    member_rebate_share: float = 0.30
    minimum_intervention_roi: float = 1.50

    # Health Scoring
    health_scoring_model_version: str = "1.0.0"
    cost_per_risk_point: int = 580

    # Compliance
    hipaa_audit_log_enabled: bool = True
    breach_notification_email: str = "security@vitanexus.com"

    # API Documentation
    enable_api_docs: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()