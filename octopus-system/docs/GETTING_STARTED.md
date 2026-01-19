# Getting Started with Octopus Architecture

**Quick start guide for local development**

---

## What You're Building

Octopus Architecture is a trust-based service marketplace that:

✅ Verifies providers with AI + human review
✅ Captures leads with cryptographic attribution
✅ Routes customers to best-fit providers
✅ Tracks bookings with dual confirmation
✅ Calculates performance-based commissions
✅ Enforces social contribution requirements

**This is not a SaaS. No subscriptions. Performance-based revenue only.**

---

## Prerequisites

### Required Software
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads/)

### Required Accounts
- **Supabase** (free tier) - [Sign up](https://supabase.com)
- **Anthropic** (API key) - [Get key](https://console.anthropic.com/)

**Estimated setup time:** 30-45 minutes

---

## Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd octopus-arch/octopus-system
```

---

## Step 2: Set Up Supabase

### 2.1 Create Project

1. Go to https://supabase.com
2. Click "New Project"
3. Name: "octopus-dev"
4. Region: Closest to you
5. Database Password: (save this)
6. Click "Create Project"

### 2.2 Run Database Schema

1. Go to SQL Editor in Supabase dashboard
2. Open `infrastructure/supabase/schema.sql` on your local machine
3. Copy entire contents
4. Paste into SQL Editor
5. Click "Run"
6. Verify all tables created (check "Table Editor")

### 2.3 Get API Keys

1. Go to Project Settings > API
2. Copy:
   - Project URL
   - Anon (public) key
   - Service (secret) key

---

## Step 3: Configure Environment

### 3.1 Create .env File

```bash
cp .env.example .env
```

### 3.2 Edit .env

```bash
# Open in your editor
nano .env  # or code .env or vim .env
```

**Required values:**

```bash
# Supabase (from Step 2.3)
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here
DATABASE_URL=postgresql://postgres:yourpassword@db.yourproject.supabase.co:5432/postgres

# API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-32-character-secret-key-here
```

**Everything else can use defaults for local development.**

---

## Step 4: Start Backend

### 4.1 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4.2 Start API Server

```bash
uvicorn api.main:app --reload
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 4.3 Test API

Open browser to:
- **API Root:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

**You should see API documentation and health status.**

---

## Step 5: Start Frontend

### 5.1 Install Dependencies

Open **new terminal** (keep API running):

```bash
cd frontend
npm install
```

### 5.2 Configure Frontend .env

```bash
# Create frontend env
nano .env.local
```

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://yourproject.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### 5.3 Start Frontend

```bash
npm run dev
```

**You should see:**
```
Local:        http://localhost:3000
Network:      http://192.168.1.x:3000
```

### 5.4 Open Frontend

Open browser to:
- **Frontend:** http://localhost:3000

**You should see the Octopus Architecture homepage.**

---

## Step 6: Start Supporting Services (Docker)

### 6.1 Start Infrastructure

Open **new terminal**:

```bash
cd octopus-system
docker-compose up -d postgres redis
```

### 6.2 Verify Services

```bash
docker-compose ps
```

**You should see:**
```
NAME                    STATUS
octopus-postgres        Up
octopus-redis           Up
```

---

## Step 7: Load Seed Data

### 7.1 Load Seattle Data

```bash
cd backend
python scripts/load_seed_data.py --file ../data/seattle/seed_data.json
```

**This loads:**
- Seattle place record
- 11 service niches
- 6 contribution types
- 2 sample providers

### 7.2 Verify Data

Open Supabase Table Editor:
- Check `places` table → Should see "Seattle Metro"
- Check `providers` table → Should see 2 sample providers

---

## Step 8: Test Core Workflows

### 8.1 Provider Search

**Via API Docs:**
1. Go to http://localhost:8000/docs
2. Find `GET /api/v1/providers/search`
3. Click "Try it out"
4. Enter:
   - `service`: "roofing"
   - `city`: "Seattle"
   - `min_trust_score`: 70
5. Click "Execute"

**Expected result:** List of providers matching criteria

### 8.2 Lead Capture

**Via API Docs:**
1. Find `POST /api/v1/leads/capture`
2. Click "Try it out"
3. Enter JSON:
```json
{
  "provider_id": "provider-id-from-search",
  "customer_name": "Test Customer",
  "customer_email": "test@example.com",
  "customer_phone": "+1-206-555-0100",
  "service_requested": "Roof repair",
  "message": "Need estimate for roof repair",
  "preferred_contact_method": "email",
  "attribution_source": "web"
}
```
4. Click "Execute"

**Expected result:** Lead created with attribution hash

---

## Step 9: Start Agent Orchestration (Optional)

### 9.1 Start Agent Services

```bash
docker-compose up -d openhands agent-zero
```

### 9.2 Test Trust Score Calculation

```bash
cd agents/orchestrator
python orchestrator.py
```

**Expected result:** Trust score calculation runs successfully

---

## Step 10: Access Admin Tools

### 10.1 Monitoring (Grafana)

```bash
docker-compose up -d prometheus grafana
```

Open:
- **Grafana:** http://localhost:3004
- **Login:** admin / admin

### 10.2 Database Studio

Go to Supabase dashboard:
- **SQL Editor:** Write custom queries
- **Table Editor:** View and edit data directly
- **API Logs:** See all API requests

---

## Development Workflow

### Making Changes

**Backend changes:**
```bash
# Edit files in backend/
# API automatically reloads (--reload flag)
# Check logs in terminal
```

**Frontend changes:**
```bash
# Edit files in frontend/
# Next.js automatically reloads
# Check browser console for errors
```

**Database changes:**
```bash
# Edit infrastructure/supabase/schema.sql
# Rerun in Supabase SQL Editor
# Or use migration tools
```

### Testing

**Backend tests:**
```bash
cd backend
pytest
```

**Frontend tests:**
```bash
cd frontend
npm test
```

---

## Common Issues & Solutions

### Issue: API won't start
**Error:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: Database connection error
**Error:** `could not connect to server`
**Solution:**
- Check `DATABASE_URL` in `.env`
- Verify Supabase project is active
- Check network connectivity

### Issue: Frontend won't build
**Error:** `Cannot find module 'next'`
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Docker containers won't start
**Error:** `port is already allocated`
**Solution:**
```bash
# Find and kill process using port
lsof -ti:5432 | xargs kill -9
# Or change port in docker-compose.yml
```

---

## What's Next?

### Learn the System

1. **Read the docs:**
   - [Architecture Overview](./ARCHITECTURE.md)
   - [API Reference](http://localhost:8000/docs)
   - [Agent Protocols](../agents/protocols/LLMS.txt)

2. **Explore the code:**
   - Backend API: `backend/api/`
   - Database models: `backend/models/`
   - Agent orchestration: `agents/orchestrator/`
   - Frontend components: `frontend/components/`

3. **Understand trust scoring:**
   - Read `backend/services/trust_scorer.py`
   - Review algorithm in `agents/protocols/trust-scorer.txt`

### Build Your First Feature

**Example: Add a new service niche**

1. Add to `data/seattle/seed_data.json`:
```json
{
  "slug": "hvac",
  "name": "HVAC",
  "description": "Heating and cooling services",
  "icon": "❄️",
  "avg_job_value": 3500,
  "keywords": ["heating", "cooling", "AC repair"]
}
```

2. Reload seed data
3. Test search with new niche
4. Update frontend UI to display it

---

## Getting Help

### Documentation
- **Full docs:** [./docs/](./docs/)
- **API reference:** http://localhost:8000/docs
- **Agent protocols:** [../agents/protocols/](../agents/protocols/)

### Community
- **GitHub Issues:** Report bugs
- **Discussions:** Ask questions
- **Slack:** (coming soon)

### Support
- **Email:** dev@octopus-arch.com

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Code style guide
- Pull request process
- Development best practices
- Testing requirements

---

## Production Deployment

When you're ready to deploy:

1. Read [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. Set up production infrastructure
3. Configure production environment
4. Run security hardening
5. Launch! 🚀

---

**You're all set! Welcome to Octopus Architecture.** 🐙

Now go build something that makes service marketplaces trustworthy again.
