# Octopus Architecture - Master Directory System

> **A trust-based, agent-driven smart directory for any city, any niche**

**Version:** 1.0.0
**Target City:** Seattle Metro & I-5 Corridor
**Company Type:** Washington State Social Purpose Corporation

---

## Executive Summary

Octopus Architecture is not a directory. It's a data-first, trust-gated marketplace with:

- **Human-verified supply** - No fake listings, no bots
- **Edge-secured lead capture** - Attribution from first touch to booking
- **Agent-aware booking flows** - AI agents can interact natively
- **Schema-native surfaces** - Schema.org + JSON-LD everywhere
- **Viral UGC loops** - Members create value through contribution
- **Performance-based monetization** - No subscriptions, only results
- **Social purpose mandate** - Every member gives back locally

## Architecture Overview

### The "Octopus" Model

```
┌─────────────────────────────────────────────────┐
│              Control Plane (Head)                │
│  OpenHands + Agent Zero + Diffy + Lightning     │
└─────────────┬───────────────────────────────────┘
              │
     ┌────────┼────────┐
     ▼        ▼        ▼
  ┌─────┐  ┌─────┐  ┌─────┐
  │Arm 1│  │Arm 2│  │Arm 3│  ... (Each = City + Niche)
  │SEA  │  │PDX  │  │SF   │
  └─────┘  └─────┘  └─────┘
```

**Each arm is:**
- One city/region
- One vertical set (roofing, construction, catering, etc.)
- One data loop
- One reputation graph
- One lead funnel

**All arms share:**
- Same schemas
- Same rules
- Same agent protocols
- Same monetization logic

## Core Primitives

Every implementation uses these seven primitives:

1. **Place** - Geographic location with boundaries
2. **Provider** - Verified business/individual
3. **Listing** - Service offering
4. **Lead/Intent** - Customer inquiry
5. **Trust Score** - Reputation metric
6. **Contribution** - Social giveback requirement
7. **Agent Verdict** - AI-driven decision

Everything else is decoration.

## Tech Stack

### Backend
- **Language:** Python 3.12+
- **API Framework:** FastAPI
- **Database:** PostgreSQL (via Supabase)
- **Cache:** Redis
- **Task Queue:** Celery (future)

### Frontend
- **Framework:** Next.js 14+
- **Library:** React 18+
- **Styling:** Tailwind CSS
- **Database Client:** Supabase JS
- **Prerendering:** ISR + Edge

### Agent Orchestration
- **Execution Spine:** OpenHands
- **Orchestrator:** Agent Zero
- **Testing/Diff:** Diffy
- **Monitoring:** Microsoft Lightning Agent
- **Negotiation:** Venice AI

### Infrastructure
- **Containers:** Docker + Docker Compose
- **Hosting:** VPS (Hetzner/OVH recommended)
- **CDN/WAF:** Cloudflare
- **CI/CD:** GitHub Actions

### Supporting Services
- **Crawling:** Firecrawl
- **Social:** Postiz
- **E-Signature:** DocuSeal
- **Translation:** LibreTranslate

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- Supabase account (or self-host)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd octopus-system

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Start infrastructure
docker-compose up -d

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run migrations
python migrate.py

# Start backend
uvicorn api.main:app --reload

# Install frontend dependencies
cd ../frontend
npm install

# Start frontend
npm run dev
```

Visit:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Supabase Studio: http://localhost:54323

## Directory Structure

```
octopus-system/
├── backend/              # FastAPI backend
│   ├── api/             # API routes
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── agents/          # Agent connectors
│   └── migrations/      # Database migrations
├── frontend/            # Next.js frontend
│   ├── components/      # React components
│   ├── pages/          # Next.js pages
│   ├── lib/            # Utilities
│   └── public/         # Static assets
├── agents/              # Agent orchestration
│   ├── orchestrator/   # Agent Zero integration
│   ├── workers/        # Specialized agents
│   └── protocols/      # LLMS.txt files
├── infrastructure/      # Deployment configs
│   ├── docker/         # Dockerfiles
│   ├── supabase/       # Database schemas
│   └── nginx/          # Reverse proxy
├── business/            # Business documents
│   ├── investor-deck/  # Pitch materials
│   ├── wa-state-filing/ # Incorporation docs
│   └── financials/     # Revenue models
├── legal/               # Legal documents
│   ├── policies/       # Privacy policy
│   ├── terms/          # Terms of service
│   └── disclosures/    # Agent disclosure
└── data/                # Seed data
    └── seattle/        # Seattle-specific data
```

## Seattle Implementation (P0)

### Target Niches
1. Roofing
2. Construction
3. Plumbing
4. Painting
5. Pressure Washing
6. Graffiti Removal (master service)
7. Ghost Kitchens
8. Catering
9. Art & Murals
10. Moving
11. Staging (luxury)

### Geographic Coverage
- Seattle proper
- Eastside (Bellevue, Redmond, Kirkland)
- South (Renton, Kent, Federal Way)
- North (Shoreline, Lynnwood, Everett)
- I-5 corridor (full stretch)

### Multilingual Support
- English (primary)
- Spanish
- Ukrainian
- Russian
- Korean
- Japanese
- Chinese (Simplified & Traditional)

## Agent Protocols

All agents communicate via LLMS.txt protocol:

```
/agents/protocols/LLMS.txt          - Main protocol
/agents/protocols/lead-router.txt   - Lead routing
/agents/protocols/trust-scorer.txt  - Trust calculation
/agents/protocols/booking-agent.txt - Booking flow
/agents/protocols/contract-gen.txt  - Contract generation
```

Agents can read these files to understand how to interact with the system.

## Trust System

### Entry Flow
1. Provider scans QR code or receives digital invitation
2. Webhook captures entry
3. Agent runs verification:
   - Business crawl (Firecrawl)
   - Reddit scrape
   - Twitter/X scan (Grok API)
   - Review entropy detection
   - AI-content detection
4. Trust score calculated
5. Manual review (if borderline)
6. Approval or rejection

### Lead Tracking
Every lead gets:
- Signed URL
- Attribution hash (SHA-256)
- Timestamp
- Stored in immutable ledger

Booking only counts if:
- It flows through system
- Webhook confirms
- Provider acknowledges

## Revenue Model

### No Subscriptions
- Zero monthly fees
- Zero listing fees
- Zero "premium" upsells

### Performance-Based
- 3-7% of booked job value
- Only charged on confirmed completion
- Provider confirms + customer confirms
- Disputed charges go to arbitration

### Why This Works
- Aligned incentives
- No churn pressure
- No feature bloat
- Boring, compounding revenue

## Social Purpose Requirement

**Every member must contribute** to one of these local projects:

- Graffiti removal (public spaces)
- Community murals
- Housing support
- Food bank logistics
- Language support (translation)
- Digital literacy training

This is tracked and enforced as part of membership.

## Replication Blueprint

### To Clone to New City

1. **Copy this repo:**
   ```bash
   git clone <this-repo> octopus-[city]
   cd octopus-[city]
   ```

2. **Update configuration:**
   ```bash
   # Edit .env
   CITY_NAME="Portland"
   CITY_SLUG="pdx"
   GEOGRAPHIC_CENTER="45.5152,-122.6784"
   ```

3. **Customize niches:**
   - Edit `data/[city]/niches.json`
   - Define local categories

4. **Load seed data:**
   ```bash
   python scripts/seed_city.py --city pdx
   ```

5. **Deploy:**
   ```bash
   docker-compose up -d
   ```

That's it. Same code, different city.

## Development Workflow

### Ralph Wiggums Loop
```
Build → Test → Diff → Improve → Repeat
```

1. **Build:** Implement feature
2. **Test:** Run automated tests
3. **Diff:** Use Diffy to compare against baseline
4. **Improve:** Fix regressions
5. **Repeat:** Until all tests pass

Diffy implements the "75% wins, 25% dies" logic:
- If new version beats baseline 75% of the time: ship it
- Otherwise: kill it and try again

## API Reference

Full API documentation available at `/docs` when running backend.

Key endpoints:
- `POST /api/v1/providers/claim` - Claim business
- `POST /api/v1/leads/capture` - Capture lead
- `GET /api/v1/trust/{provider_id}` - Get trust score
- `POST /api/v1/bookings/confirm` - Confirm booking

## Security

- **RLS:** Row-level security on all Supabase tables
- **Edge functions:** No public database writes
- **Signed URLs:** All lead capture uses signed URLs
- **Rate limiting:** Redis-backed rate limiter
- **Input validation:** Pydantic models everywhere
- **Secret management:** All secrets in env vars, never committed

## Contributing

This is a social purpose company. Contributions are welcome.

See `CONTRIBUTING.md` for guidelines.

## License

Proprietary - Social Purpose Corporation

See `LICENSE.md` for full terms.

## Support

- **Documentation:** `/docs`
- **Issues:** GitHub Issues
- **Email:** support@octopus-arch.com
- **Slack:** (coming soon)

---

## Kevin O'Leary Pitch (One Line)

**"We don't sell ads. We don't sell software. We deliver verified customers to verified businesses — and we only get paid when they win."**

---

Built with OpenHands • Powered by Claude Sonnet 4.5
