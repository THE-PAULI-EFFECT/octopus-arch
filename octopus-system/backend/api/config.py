"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Octopus Architecture"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # City Configuration (Seattle P0)
    CITY_NAME: str = "Seattle"
    CITY_SLUG: str = "sea"
    CITY_TIMEZONE: str = "America/Los_Angeles"
    GEOGRAPHIC_CENTER: str = "47.6062,-122.3321"  # Seattle coordinates
    GEOGRAPHIC_RADIUS_KM: int = 80  # I-5 corridor coverage

    # Security
    SECRET_KEY: str
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://octopus-sea.com",
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "octopus-sea.com"]

    # Database (Supabase)
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # AI/Agent Configuration
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # OpenHands Integration
    OPENHANDS_API_URL: str = "http://localhost:3001"
    OPENHANDS_API_KEY: str = ""

    # Agent Zero
    AGENT_ZERO_URL: str = "http://localhost:5000"

    # Firecrawl
    FIRECRAWL_API_KEY: str = ""

    # E-Signature (DocuSeal)
    DOCUSEAL_API_URL: str = "http://localhost:3002"
    DOCUSEAL_API_KEY: str = ""

    # Social (Postiz)
    POSTIZ_API_URL: str = "http://localhost:5001"
    POSTIZ_API_KEY: str = ""

    # Trust & Verification
    TRUST_SCORE_MIN: int = 60  # Minimum score to be listed
    TRUST_SCORE_MAX: int = 100
    MANUAL_REVIEW_THRESHOLD: int = 70  # Below this, manual review required

    # Lead Attribution
    LEAD_URL_EXPIRY_HOURS: int = 72  # Signed URLs expire after 3 days
    LEAD_ATTRIBUTION_WINDOW_DAYS: int = 30  # Attribution window

    # Revenue
    COMMISSION_RATE_MIN: float = 0.03  # 3%
    COMMISSION_RATE_MAX: float = 0.07  # 7%
    COMMISSION_RATE_DEFAULT: float = 0.05  # 5%

    # Social Purpose
    CONTRIBUTION_REQUIRED: bool = True
    CONTRIBUTION_MIN_HOURS_YEAR: int = 12  # 1 hour per month

    # Multilingual
    SUPPORTED_LANGUAGES: List[str] = [
        "en",  # English
        "es",  # Spanish
        "uk",  # Ukrainian
        "ru",  # Russian
        "ko",  # Korean
        "ja",  # Japanese
        "zh",  # Chinese
    ]
    DEFAULT_LANGUAGE: str = "en"

    # Monitoring
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    # Email (Future)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
