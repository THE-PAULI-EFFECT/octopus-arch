"""
Pydantic models for Octopus Architecture
Core primitives: Place, Provider, Listing, Lead, Trust Score, Contribution, Agent Verdict
"""

from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import uuid


# Enums
class ProviderStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class LeadStatus(str, Enum):
    CAPTURED = "captured"
    CONTACTED = "contacted"
    QUOTED = "quoted"
    BOOKED = "booked"
    COMPLETED = "completed"
    LOST = "lost"


class BookingStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class ContributionType(str, Enum):
    GRAFFITI_REMOVAL = "graffiti_removal"
    COMMUNITY_MURAL = "community_mural"
    HOUSING_SUPPORT = "housing_support"
    FOOD_BANK = "food_bank"
    TRANSLATION = "translation"
    DIGITAL_LITERACY = "digital_literacy"


# Core Primitive 1: Place
class Place(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    slug: str
    city: str
    state: str = "WA"
    country: str = "USA"
    latitude: float
    longitude: float
    timezone: str = "America/Los_Angeles"
    radius_km: int = 80
    population: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Core Primitive 2: Provider
class ProviderBase(BaseModel):
    business_name: str
    contact_name: str
    email: EmailStr
    phone: str
    website: Optional[HttpUrl] = None
    description: str
    services: List[str]
    service_area_cities: List[str]
    years_in_business: Optional[int] = None


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    business_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[HttpUrl] = None
    description: Optional[str] = None
    services: Optional[List[str]] = None
    service_area_cities: Optional[List[str]] = None


class Provider(ProviderBase):
    id: str
    status: ProviderStatus
    trust_score: int = 0
    place_id: str
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Core Primitive 3: Listing
class ListingBase(BaseModel):
    title: str
    description: str
    service_category: str
    price_type: str = Field(..., description="fixed, hourly, quote")
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    price_currency: str = "USD"
    images: Optional[List[HttpUrl]] = []
    tags: Optional[List[str]] = []


class ListingCreate(ListingBase):
    provider_id: str


class Listing(ListingBase):
    id: str
    provider_id: str
    is_active: bool = True
    views: int = 0
    leads_count: int = 0
    bookings_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Core Primitive 4: Lead / Intent
class LeadBase(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    service_requested: str
    message: Optional[str] = None
    preferred_contact_method: str = "email"
    preferred_date: Optional[datetime] = None
    budget_range: Optional[str] = None


class LeadCreate(LeadBase):
    provider_id: str
    listing_id: Optional[str] = None
    attribution_source: Optional[str] = None  # QR code, web, agent, etc.


class Lead(LeadBase):
    id: str
    provider_id: str
    listing_id: Optional[str]
    status: LeadStatus
    attribution_hash: str  # SHA-256 hash for tracking
    attribution_source: Optional[str]
    signed_url: Optional[str]
    signed_url_expires_at: Optional[datetime]
    contacted_at: Optional[datetime]
    quoted_at: Optional[datetime]
    booked_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Core Primitive 5: Trust Score
class TrustScoreBase(BaseModel):
    provider_id: str
    score: int = Field(..., ge=0, le=100)
    factors: Dict[str, float]  # Breakdown of score components


class TrustScore(TrustScoreBase):
    id: str
    business_crawl_score: Optional[int] = None
    review_entropy_score: Optional[int] = None
    social_presence_score: Optional[int] = None
    verification_score: Optional[int] = None
    contribution_score: Optional[int] = None
    needs_manual_review: bool = False
    manual_review_notes: Optional[str] = None
    calculated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Core Primitive 6: Contribution (Social Purpose)
class ContributionBase(BaseModel):
    provider_id: str
    contribution_type: ContributionType
    hours: float
    description: str
    date: datetime


class ContributionCreate(ContributionBase):
    pass


class Contribution(ContributionBase):
    id: str
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Core Primitive 7: Agent Verdict
class AgentVerdictBase(BaseModel):
    entity_type: str  # provider, lead, booking, etc.
    entity_id: str
    agent_name: str
    verdict: str  # approved, rejected, flagged, etc.
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    data: Optional[Dict] = {}


class AgentVerdict(AgentVerdictBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Booking Models
class BookingBase(BaseModel):
    lead_id: str
    provider_id: str
    customer_name: str
    service_description: str
    scheduled_date: datetime
    estimated_value: float
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    scheduled_date: Optional[datetime] = None
    actual_value: Optional[float] = None
    notes: Optional[str] = None


class Booking(BookingBase):
    id: str
    status: BookingStatus
    actual_value: Optional[float] = None
    commission_rate: float = 0.05
    commission_amount: Optional[float] = None
    provider_confirmed_at: Optional[datetime] = None
    customer_confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# API Response Models
class HealthCheck(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: float


class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    message: Optional[str] = None


# Search Models
class ProviderSearchQuery(BaseModel):
    query: Optional[str] = None
    service: Optional[str] = None
    city: Optional[str] = None
    min_trust_score: int = 60
    limit: int = 20
    offset: int = 0


class ProviderSearchResult(BaseModel):
    providers: List[Provider]
    total: int
    limit: int
    offset: int
