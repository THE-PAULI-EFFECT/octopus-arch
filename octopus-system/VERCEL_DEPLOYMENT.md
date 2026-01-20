# Vercel Deployment Guide - Octopus Architecture

## Option 1: Deploy via Vercel Dashboard (Recommended - Fastest)

### Step 1: Import GitHub Repository

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click "Import Git Repository"
3. Select: `THE-PAULI-EFFECT/octopus-arch`
4. **Root Directory:** Change to `octopus-system/frontend`
5. **Framework Preset:** Next.js (should auto-detect)

### Step 2: Configure Environment Variables

Add these environment variables in Vercel dashboard:

```bash
# From your master.env file
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# Optional: Backend API URL (leave default for static preview)
NEXT_PUBLIC_API_URL=https://your-api-url.com
```

### Step 3: Deploy

1. Click "Deploy"
2. Wait 2-3 minutes
3. Get your live URL: `https://octopus-architecture.vercel.app`

---

## Option 2: Deploy via Vercel CLI

### Step 1: Login to Vercel

```bash
vercel login
```

### Step 2: Navigate to Frontend

```bash
cd E:\THE PAULI FILES\octopus-arch\octopus-system\frontend
```

### Step 3: Deploy

```bash
# Production deployment
vercel --prod

# Or with environment variables
vercel --prod \
  -e NEXT_PUBLIC_SUPABASE_URL="your-url" \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY="your-key"
```

---

## Option 3: Deploy via Vercel Token

If you have a Vercel token in your master.env:

### Step 1: Set Token

```bash
# Windows PowerShell
$env:VERCEL_TOKEN="your-vercel-token-here"

# Or Windows CMD
set VERCEL_TOKEN=your-vercel-token-here
```

### Step 2: Deploy

```bash
cd octopus-system\frontend
vercel --prod --token %VERCEL_TOKEN% --yes
```

---

## Environment Variables Reference

These variables from your `master.env` are needed:

```bash
# Supabase (Required for database access)
NEXT_PUBLIC_SUPABASE_URL=https://yourproject.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...your-anon-key

# API Backend (Optional - can add later)
NEXT_PUBLIC_API_URL=https://octopus-api.vercel.app

# Vercel Token (Optional - for CLI deployment)
VERCEL_TOKEN=your-vercel-token
```

---

## After Deployment

### 1. Test Your Deployment

Visit your Vercel URL:
- Frontend: `https://octopus-architecture-xxx.vercel.app`
- You should see the Octopus Architecture landing page

### 2. Add Custom Domain (Optional)

1. Go to Project Settings > Domains
2. Add: `octopus-sea.com`
3. Configure DNS as instructed

### 3. Deploy Backend API (Separate)

The backend FastAPI needs to be deployed separately:
- **Recommended:** Render.com, Railway.app, or Fly.io
- **Alternative:** Vercel Serverless Functions (requires adaptation)

---

## Quick Deploy Button

Alternatively, click this button:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/THE-PAULI-EFFECT/octopus-arch&root-directory=octopus-system/frontend&env=NEXT_PUBLIC_SUPABASE_URL,NEXT_PUBLIC_SUPABASE_ANON_KEY)

---

## Troubleshooting

### "Build Failed"
- Check that root directory is set to `octopus-system/frontend`
- Verify all dependencies are in package.json

### "Environment Variables Missing"
- Add them in Vercel Dashboard → Settings → Environment Variables
- Redeploy after adding

### "API Not Connected"
- API is separate deployment - frontend will work without it
- API status will show as "Backend not running" (expected for static preview)

---

## Expected Result

✅ Live URL in 2-3 minutes
✅ Beautiful landing page with Octopus Architecture branding
✅ System status dashboard
✅ Feature overview and business model stats
✅ Links to documentation and GitHub

---

**Next Steps:**
1. Deploy frontend to Vercel (2 minutes)
2. Deploy backend to Render/Railway (10 minutes)
3. Connect custom domain (5 minutes)
4. You're live! 🚀
