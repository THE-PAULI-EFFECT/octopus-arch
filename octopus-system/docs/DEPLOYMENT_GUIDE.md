# Octopus Architecture - Deployment Guide

**Production Deployment Guide for Seattle P0 Launch**

---

## Overview

This guide walks through deploying the complete Octopus Architecture system to production. We recommend a VPS-based deployment (Hetzner, OVH) with Cloudflare for CDN/WAF.

**Estimated Setup Time:** 4-6 hours
**Monthly Cost (Seattle P0):** $150-250

---

## Prerequisites

### Required Accounts
- [ ] Supabase account (or self-hosted Postgres)
- [ ] Cloudflare account (free tier sufficient)
- [ ] VPS provider (Hetzner, OVH, DigitalOcean)
- [ ] Domain name (e.g., octopus-sea.com)
- [ ] Anthropic API key (Claude Sonnet 4.5)
- [ ] OpenAI API key (optional, for GPT models)

### Required Software (Local)
- Docker & Docker Compose
- Git
- SSH client
- Domain DNS access

---

## Phase 1: Infrastructure Setup

### 1.1 Provision VPS

**Recommended Specs (Seattle P0):**
- **CPU:** 4 cores
- **RAM:** 16 GB
- **Storage:** 160 GB SSD
- **Bandwidth:** 10 TB/month
- **Location:** US West Coast (Oregon, California)

**Providers:**
- Hetzner: CPX41 ($28/month)
- OVH: B2-30 ($35/month)
- DigitalOcean: 4 CPU / 16 GB ($96/month)

**OS:** Ubuntu 22.04 LTS

### 1.2 Initial Server Setup

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Create deploy user
adduser deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Set up firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Switch to deploy user
su - deploy
```

---

## Phase 2: Supabase Setup

### 2.1 Create Supabase Project

1. Go to https://supabase.com
2. Create new project: "octopus-seattle"
3. Choose region: US West
4. Note down:
   - Project URL
   - Anon key
   - Service key
   - Database password

### 2.2 Run Database Migrations

```bash
# Copy schema.sql to local machine
# Then run in Supabase SQL Editor:

# Go to: Project > SQL Editor
# Paste contents of infrastructure/supabase/schema.sql
# Run query
```

### 2.3 Enable Row Level Security

Verify RLS is enabled on all tables:
```sql
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';
```

All `rowsecurity` should be `true`.

---

## Phase 3: Domain & SSL Setup

### 3.1 DNS Configuration (Cloudflare)

Add DNS records:

```
Type    Name          Value                   Proxy
A       @             your-server-ip          Proxied
A       www           your-server-ip          Proxied
A       api           your-server-ip          Proxied
CNAME   admin         @                       Proxied
```

### 3.2 SSL Certificate

Cloudflare provides automatic SSL (Universal SSL).

**SSL/TLS Mode:** Full (strict)

---

## Phase 4: Application Deployment

### 4.1 Clone Repository

```bash
cd /home/deploy
git clone <your-repo-url> octopus
cd octopus/octopus-system
```

### 4.2 Configure Environment

```bash
# Copy example env
cp .env.example .env

# Edit with production values
nano .env
```

**Critical variables:**
```bash
ENVIRONMENT=production
SECRET_KEY=<generate-strong-32-char-key>
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_KEY=<your-service-key>
DATABASE_URL=postgresql://postgres:<password>@db.your-project.supabase.co:5432/postgres
REDIS_URL=redis://redis:6379/0
ANTHROPIC_API_KEY=<your-key>
ALLOWED_ORIGINS=https://octopus-sea.com,https://www.octopus-sea.com
ALLOWED_HOSTS=octopus-sea.com,www.octopus-sea.com
```

**Generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 4.3 Start Services

```bash
# Build and start all services
docker-compose up -d

# Verify all containers are running
docker-compose ps

# Check logs
docker-compose logs -f api
docker-compose logs -f frontend
```

**Expected containers:**
- octopus-postgres
- octopus-redis
- octopus-api
- octopus-frontend
- octopus-openhands
- octopus-agent-zero
- octopus-firecrawl
- octopus-docuseal
- octopus-postiz

---

## Phase 5: Reverse Proxy (Nginx)

### 5.1 Install Nginx

```bash
sudo apt install nginx -y
```

### 5.2 Configure Sites

**Frontend (octopus-sea.com):**

```bash
sudo nano /etc/nginx/sites-available/octopus-frontend
```

```nginx
server {
    listen 80;
    server_name octopus-sea.com www.octopus-sea.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**API (api.octopus-sea.com):**

```bash
sudo nano /etc/nginx/sites-available/octopus-api
```

```nginx
server {
    listen 80;
    server_name api.octopus-sea.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }
}

# Rate limit zone
limit_req_zone $binary_remote_addr zone=api:10m rate=60r/m;
```

### 5.3 Enable Sites

```bash
sudo ln -s /etc/nginx/sites-available/octopus-frontend /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/octopus-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Phase 6: Monitoring & Logging

### 6.1 Enable Prometheus/Grafana

Already included in docker-compose.yml.

Access Grafana:
- URL: http://your-server-ip:3004
- Default: admin / admin

### 6.2 Configure Sentry (Optional)

```bash
# Add to .env
SENTRY_DSN=<your-sentry-dsn>

# Restart services
docker-compose restart api frontend
```

### 6.3 Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/octopus
```

```
/home/deploy/octopus/octopus-system/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 deploy deploy
    sharedscripts
}
```

---

## Phase 7: Backups

### 7.1 Database Backups (Automated)

Supabase includes automated backups (7-day retention on free tier).

**Manual backup:**
```bash
# Create backup script
nano /home/deploy/backup-db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec octopus-postgres pg_dump -U postgres octopus > /home/deploy/backups/octopus_$DATE.sql
# Keep last 30 days
find /home/deploy/backups -type f -mtime +30 -delete
```

```bash
chmod +x /home/deploy/backup-db.sh

# Add to crontab
crontab -e
```

```
0 2 * * * /home/deploy/backup-db.sh
```

### 7.2 Volume Backups

```bash
# Backup Redis data
docker run --rm -v octopus-system_redis_data:/data -v /home/deploy/backups:/backup ubuntu tar czf /backup/redis_backup.tar.gz /data

# Backup uploads
docker run --rm -v octopus-system_postiz_data:/data -v /home/deploy/backups:/backup ubuntu tar czf /backup/uploads_backup.tar.gz /data
```

---

## Phase 8: Security Hardening

### 8.1 Fail2Ban

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 8.2 Automatic Updates

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 8.3 SSH Hardening

```bash
sudo nano /etc/ssh/sshd_config
```

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

```bash
sudo systemctl restart sshd
```

---

## Phase 9: Testing & Verification

### 9.1 Health Checks

```bash
# API health
curl https://api.octopus-sea.com/health

# Frontend
curl -I https://octopus-sea.com

# Database connectivity
docker exec octopus-postgres pg_isready

# Redis
docker exec octopus-redis redis-cli ping
```

### 9.2 Load Testing

```bash
# Install hey
go install github.com/rakyll/hey@latest

# Test API
hey -n 1000 -c 50 https://api.octopus-sea.com/health
```

### 9.3 Security Scan

```bash
# Install nikto
sudo apt install nikto -y

# Scan
nikto -h https://octopus-sea.com
```

---

## Phase 10: Launch Checklist

- [ ] All Docker containers running
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] SSL certificates active
- [ ] DNS records propagated
- [ ] API health check passing
- [ ] Frontend accessible
- [ ] Monitoring dashboards active
- [ ] Backups configured
- [ ] Security hardening complete
- [ ] Rate limiting tested
- [ ] Agent endpoints responding
- [ ] Seed data loaded

---

## Scaling Considerations

### Horizontal Scaling

**When to scale:**
- API response time > 200ms
- CPU usage > 70% sustained
- More than 10,000 providers

**How to scale:**
1. Add load balancer (Nginx, HAProxy)
2. Deploy multiple API instances
3. Use external Redis (Redis Cloud)
4. Use managed Postgres (Supabase Pro, RDS)
5. Add CDN caching (Cloudflare Caching)

### Vertical Scaling

**Upgrade path:**
1. Current: 4 CPU / 16 GB → $28/month
2. Next: 8 CPU / 32 GB → $55/month
3. Next: 16 CPU / 64 GB → $110/month

---

## Disaster Recovery

### Recovery Time Objective (RTO)
**Target:** < 4 hours

### Recovery Point Objective (RPO)
**Target:** < 24 hours

### Recovery Steps

1. **Provision new server** (30 min)
2. **Restore database** from Supabase backup (15 min)
3. **Deploy application** from git (20 min)
4. **Configure DNS** to point to new server (5 min)
5. **Verify functionality** (30 min)

---

## Support & Maintenance

### Maintenance Windows
- **Regular:** Sunday 2-4 AM PST
- **Emergency:** As needed with notification

### Monitoring Alerts

Set up alerts for:
- Server CPU > 80%
- Server memory > 90%
- Disk space < 20%
- API error rate > 5%
- Database connection failures

**Tool:** Grafana Alerting or UptimeRobot

---

## Cost Breakdown (Monthly)

| Service | Cost |
|---------|------|
| VPS (Hetzner CPX41) | $28 |
| Supabase (Free tier) | $0 |
| Cloudflare (Free tier) | $0 |
| Domain (.com) | $12/year ≈ $1/month |
| Anthropic API (est. 1M tokens) | $30 |
| Sentry (Optional) | $0 (Developer tier) |
| **Total** | **~$60/month** |

**With paid tiers:**
- Supabase Pro: +$25
- Cloudflare Pro: +$20
- **Total:** ~$105/month

---

## Next Steps After Deployment

1. **Load seed data** - Import Seattle providers
2. **Test workflows** - End-to-end booking flow
3. **Configure monitoring** - Set up Grafana dashboards
4. **Train team** - Admin panel walkthrough
5. **Soft launch** - Invite beta providers
6. **Marketing** - QR codes, SEO, social

---

## Troubleshooting

### API not responding
```bash
docker-compose logs api
docker-compose restart api
```

### Database connection errors
```bash
# Check Supabase status
# Verify DATABASE_URL in .env
# Check network connectivity
docker exec octopus-api ping db.your-project.supabase.co
```

### Redis connection errors
```bash
docker exec octopus-redis redis-cli ping
docker-compose restart redis
```

### Frontend build errors
```bash
cd frontend
npm install
npm run build
docker-compose restart frontend
```

---

**For production support:** support@octopus-arch.com
**Documentation:** https://docs.octopus-arch.com
