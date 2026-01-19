-- Octopus Architecture - Master Database Schema
-- Supabase PostgreSQL Schema with Row Level Security (RLS)
-- Version: 1.0.0

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For full-text search

-- ============================================================================
-- CORE PRIMITIVE 1: PLACES
-- ============================================================================
CREATE TABLE places (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL DEFAULT 'WA',
    country VARCHAR(50) NOT NULL DEFAULT 'USA',
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'America/Los_Angeles',
    radius_km INTEGER NOT NULL DEFAULT 80,
    population INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Geospatial index for location queries
CREATE INDEX idx_places_location ON places USING GIST (
    ST_MakePoint(longitude, latitude)::geography
);

-- ============================================================================
-- CORE PRIMITIVE 2: PROVIDERS
-- ============================================================================
CREATE TYPE provider_status AS ENUM ('pending', 'verified', 'rejected', 'suspended');

CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    place_id UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    website VARCHAR(500),
    description TEXT NOT NULL,
    services TEXT[] NOT NULL,
    service_area_cities TEXT[] NOT NULL,
    years_in_business INTEGER,
    status provider_status NOT NULL DEFAULT 'pending',
    trust_score INTEGER DEFAULT 0 CHECK (trust_score >= 0 AND trust_score <= 100),
    verified_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_providers_place ON providers(place_id);
CREATE INDEX idx_providers_status ON providers(status);
CREATE INDEX idx_providers_trust_score ON providers(trust_score);
CREATE INDEX idx_providers_services ON providers USING GIN(services);
CREATE INDEX idx_providers_search ON providers USING GIN(
    to_tsvector('english', business_name || ' ' || description)
);

-- ============================================================================
-- CORE PRIMITIVE 3: LISTINGS
-- ============================================================================
CREATE TYPE price_type AS ENUM ('fixed', 'hourly', 'quote');

CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    price_type price_type NOT NULL,
    price_min DECIMAL(10, 2),
    price_max DECIMAL(10, 2),
    price_currency VARCHAR(3) DEFAULT 'USD',
    images TEXT[],
    tags TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    views INTEGER DEFAULT 0,
    leads_count INTEGER DEFAULT 0,
    bookings_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_listings_provider ON listings(provider_id);
CREATE INDEX idx_listings_category ON listings(service_category);
CREATE INDEX idx_listings_active ON listings(is_active);
CREATE INDEX idx_listings_tags ON listings USING GIN(tags);

-- ============================================================================
-- CORE PRIMITIVE 4: LEADS / INTENTS
-- ============================================================================
CREATE TYPE lead_status AS ENUM (
    'captured', 'contacted', 'quoted', 'booked', 'completed', 'lost'
);

CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    listing_id UUID REFERENCES listings(id) ON DELETE SET NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(50) NOT NULL,
    service_requested VARCHAR(255) NOT NULL,
    message TEXT,
    preferred_contact_method VARCHAR(50) DEFAULT 'email',
    preferred_date TIMESTAMP WITH TIME ZONE,
    budget_range VARCHAR(100),
    status lead_status NOT NULL DEFAULT 'captured',
    attribution_hash VARCHAR(64) UNIQUE NOT NULL, -- SHA-256 hash
    attribution_source VARCHAR(100), -- QR code, web, agent, etc.
    signed_url TEXT,
    signed_url_expires_at TIMESTAMP WITH TIME ZONE,
    contacted_at TIMESTAMP WITH TIME ZONE,
    quoted_at TIMESTAMP WITH TIME ZONE,
    booked_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_leads_provider ON leads(provider_id);
CREATE INDEX idx_leads_listing ON leads(listing_id);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_attribution ON leads(attribution_hash);
CREATE INDEX idx_leads_created ON leads(created_at DESC);

-- ============================================================================
-- CORE PRIMITIVE 5: TRUST SCORES
-- ============================================================================
CREATE TABLE trust_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    factors JSONB NOT NULL, -- Breakdown of score components
    business_crawl_score INTEGER,
    review_entropy_score INTEGER,
    social_presence_score INTEGER,
    verification_score INTEGER,
    contribution_score INTEGER,
    needs_manual_review BOOLEAN DEFAULT FALSE,
    manual_review_notes TEXT,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_trust_scores_provider ON trust_scores(provider_id);
CREATE INDEX idx_trust_scores_calculated ON trust_scores(calculated_at DESC);
CREATE INDEX idx_trust_scores_needs_review ON trust_scores(needs_manual_review);

-- ============================================================================
-- CORE PRIMITIVE 6: CONTRIBUTIONS (Social Purpose)
-- ============================================================================
CREATE TYPE contribution_type AS ENUM (
    'graffiti_removal',
    'community_mural',
    'housing_support',
    'food_bank',
    'translation',
    'digital_literacy'
);

CREATE TABLE contributions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    contribution_type contribution_type NOT NULL,
    hours DECIMAL(5, 2) NOT NULL,
    description TEXT NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES providers(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_contributions_provider ON contributions(provider_id);
CREATE INDEX idx_contributions_type ON contributions(contribution_type);
CREATE INDEX idx_contributions_verified ON contributions(verified);

-- ============================================================================
-- CORE PRIMITIVE 7: AGENT VERDICTS
-- ============================================================================
CREATE TABLE agent_verdicts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL, -- provider, lead, booking, etc.
    entity_id UUID NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    verdict VARCHAR(50) NOT NULL, -- approved, rejected, flagged, etc.
    confidence DECIMAL(3, 2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    reasoning TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_agent_verdicts_entity ON agent_verdicts(entity_type, entity_id);
CREATE INDEX idx_agent_verdicts_agent ON agent_verdicts(agent_name);
CREATE INDEX idx_agent_verdicts_created ON agent_verdicts(created_at DESC);

-- ============================================================================
-- BOOKINGS
-- ============================================================================
CREATE TYPE booking_status AS ENUM (
    'requested', 'confirmed', 'in_progress', 'completed', 'cancelled', 'disputed'
);

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    customer_name VARCHAR(255) NOT NULL,
    service_description TEXT NOT NULL,
    scheduled_date TIMESTAMP WITH TIME ZONE NOT NULL,
    estimated_value DECIMAL(10, 2) NOT NULL,
    actual_value DECIMAL(10, 2),
    commission_rate DECIMAL(4, 3) NOT NULL DEFAULT 0.05, -- 5%
    commission_amount DECIMAL(10, 2),
    status booking_status NOT NULL DEFAULT 'requested',
    provider_confirmed_at TIMESTAMP WITH TIME ZONE,
    customer_confirmed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_bookings_lead ON bookings(lead_id);
CREATE INDEX idx_bookings_provider ON bookings(provider_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_scheduled ON bookings(scheduled_date);

-- ============================================================================
-- REVIEWS (Future)
-- ============================================================================
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    content TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_reviews_booking ON reviews(booking_id);
CREATE INDEX idx_reviews_provider ON reviews(provider_id);
CREATE INDEX idx_reviews_flagged ON reviews(is_flagged);

-- ============================================================================
-- UPDATED_AT TRIGGER FUNCTION
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_places_updated_at BEFORE UPDATE ON places
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_providers_updated_at BEFORE UPDATE ON providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE places ENABLE ROW LEVEL SECURITY;
ALTER TABLE providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE trust_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE contributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_verdicts ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- Public read access to verified providers
CREATE POLICY "Public can view verified providers"
    ON providers FOR SELECT
    USING (status = 'verified');

-- Public read access to active listings from verified providers
CREATE POLICY "Public can view active listings"
    ON listings FOR SELECT
    USING (is_active = TRUE AND EXISTS (
        SELECT 1 FROM providers
        WHERE providers.id = listings.provider_id
        AND providers.status = 'verified'
    ));

-- Public read access to places
CREATE POLICY "Public can view places"
    ON places FOR SELECT
    USING (TRUE);

-- Lead privacy: Only provider and system can view
CREATE POLICY "Providers can view their leads"
    ON leads FOR SELECT
    USING (auth.uid() = provider_id::TEXT::UUID);

-- Booking privacy: Only provider, customer, and system can view
CREATE POLICY "Providers can view their bookings"
    ON bookings FOR SELECT
    USING (auth.uid() = provider_id::TEXT::UUID);

-- Trust scores: Public read for verified providers
CREATE POLICY "Public can view trust scores of verified providers"
    ON trust_scores FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM providers
        WHERE providers.id = trust_scores.provider_id
        AND providers.status = 'verified'
    ));

-- Contributions: Public read (social purpose transparency)
CREATE POLICY "Public can view verified contributions"
    ON contributions FOR SELECT
    USING (verified = TRUE);

-- Reviews: Public read for non-flagged reviews
CREATE POLICY "Public can view non-flagged reviews"
    ON reviews FOR SELECT
    USING (is_flagged = FALSE);

-- ============================================================================
-- SEED DATA: Seattle
-- ============================================================================
INSERT INTO places (name, slug, city, state, country, latitude, longitude, timezone, radius_km, population)
VALUES (
    'Seattle Metro',
    'seattle',
    'Seattle',
    'WA',
    'USA',
    47.6062,
    -122.3321,
    'America/Los_Angeles',
    80,
    4018762
);

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- Provider performance view
CREATE OR REPLACE VIEW provider_performance AS
SELECT
    p.id AS provider_id,
    p.business_name,
    p.trust_score,
    COUNT(DISTINCT l.id) AS total_leads,
    COUNT(DISTINCT CASE WHEN l.status = 'completed' THEN l.id END) AS completed_leads,
    COUNT(DISTINCT b.id) AS total_bookings,
    COUNT(DISTINCT CASE WHEN b.status = 'completed' THEN b.id END) AS completed_bookings,
    COALESCE(SUM(CASE WHEN b.status = 'completed' THEN b.actual_value END), 0) AS total_revenue,
    COALESCE(SUM(CASE WHEN b.status = 'completed' THEN b.commission_amount END), 0) AS total_commission,
    COALESCE(SUM(c.hours), 0) AS contribution_hours,
    AVG(r.rating) AS average_rating,
    COUNT(r.id) AS review_count
FROM providers p
LEFT JOIN leads l ON l.provider_id = p.id
LEFT JOIN bookings b ON b.provider_id = p.id
LEFT JOIN contributions c ON c.provider_id = p.id AND c.verified = TRUE
LEFT JOIN reviews r ON r.provider_id = p.id AND r.is_flagged = FALSE
GROUP BY p.id, p.business_name, p.trust_score;

-- System health metrics view
CREATE OR REPLACE VIEW system_health AS
SELECT
    (SELECT COUNT(*) FROM providers WHERE status = 'verified') AS verified_providers,
    (SELECT COUNT(*) FROM providers WHERE status = 'pending') AS pending_providers,
    (SELECT COUNT(*) FROM leads WHERE created_at > NOW() - INTERVAL '24 hours') AS leads_today,
    (SELECT COUNT(*) FROM bookings WHERE status = 'completed' AND completed_at > NOW() - INTERVAL '24 hours') AS bookings_completed_today,
    (SELECT COALESCE(SUM(commission_amount), 0) FROM bookings WHERE status = 'completed' AND completed_at > NOW() - INTERVAL '24 hours') AS revenue_today,
    (SELECT COUNT(*) FROM trust_scores WHERE needs_manual_review = TRUE) AS pending_reviews;

-- Grant access to authenticated users
GRANT SELECT ON provider_performance TO authenticated;
GRANT SELECT ON system_health TO authenticated;
