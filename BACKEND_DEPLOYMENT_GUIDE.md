# VitaNexus Backend Deployment Guide

**Status**: Ready for deployment
**Recommended Platform**: Railway (easiest) or Render (free tier available)

---

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)

**Why Railway?**
- ✅ Automatic PostgreSQL database provisioning
- ✅ Zero-config deployments
- ✅ Free tier: $5/month credit
- ✅ Great FastAPI support

**Steps:**

1. **Login to Railway**
```bash
railway login
```

2. **Initialize Project**
```bash
cd /Users/somtonweke/Inversion\ Health/Vita
railway init
```

3. **Add PostgreSQL Database**
```bash
railway add --plugin postgresql
```

4. **Deploy**
```bash
railway up
```

5. **Get your API URL**
```bash
railway domain
```

**Railway will automatically:**
- Detect Python project
- Install requirements.txt
- Run Procfile command
- Set up DATABASE_URL environment variable
- Provide HTTPS endpoint

---

### Option 2: Render (100% Free Tier Available)

**Why Render?**
- ✅ Generous free tier
- ✅ PostgreSQL included (free)
- ✅ Zero configuration
- ✅ Automatic HTTPS

**Steps:**

1. **Go to** https://render.com and sign up

2. **Create New Web Service**
   - Connect GitHub repository (or deploy from dashboard)
   - Select "Python"
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

3. **Add PostgreSQL Database**
   - Click "New" → "PostgreSQL"
   - Name: `vitanexus-db`
   - Plan: Free

4. **Set Environment Variables**
   (See `.env.production.example` for full list)

   **Required:**
   ```
   DATABASE_URL = [provided by Render PostgreSQL]
   SECRET_KEY = [generate random string]
   JWT_SECRET_KEY = [generate random string]
   PHI_ENCRYPTION_KEY = [generate random string]
   CORS_ORIGINS = ["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]
   ENVIRONMENT = production
   DEBUG = false
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait ~5 minutes for deployment

6. **Get Your API URL**
   - Will be like: `https://vitanexus-api.onrender.com`

---

### Option 3: Vercel Serverless (Advanced)

**Note**: FastAPI on Vercel requires ASGI adapter setup. Railway/Render are easier.

If you want to use Vercel anyway:

1. Create `vercel.json` in root:
```json
{
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/main.py"
    }
  ]
}
```

2. Deploy:
```bash
vercel --prod
```

**Limitations**:
- Need external PostgreSQL (Neon, Supabase)
- Serverless cold starts
- 10-second timeout on free tier

---

## 📦 Files Ready for Deployment

All deployment files have been created:

- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Railway/Heroku startup command
- ✅ `runtime.txt` - Python version specification
- ✅ `railway.json` - Railway configuration
- ✅ `render.yaml` - Render blueprint
- ✅ `.env.production.example` - Environment variable template

---

## 🔐 Environment Variables to Set

### Required (Must Set)

```bash
# Database (auto-provided by Railway/Render)
DATABASE_URL=postgresql://user:password@host:5432/vitanexus_prod

# Security (generate random strings)
SECRET_KEY=<generate-strong-random-string>
JWT_SECRET_KEY=<generate-strong-random-string>
PHI_ENCRYPTION_KEY=<generate-strong-random-string>

# CORS (your Vercel frontend URL)
CORS_ORIGINS=["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]
```

**Generate secure keys:**
```bash
# Generate random keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Optional (Can Set Later)

```bash
# OAuth / Wearables
FITBIT_CLIENT_ID=
FITBIT_CLIENT_SECRET=
APPLE_HEALTH_TEAM_ID=
GARMIN_CONSUMER_KEY=

# Email notifications
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=

# Monitoring
DATADOG_API_KEY=
```

---

## 🗄️ Database Setup

### If Using Railway

1. Add PostgreSQL:
```bash
railway add --plugin postgresql
```

2. Get connection string:
```bash
railway variables
# Look for DATABASE_URL
```

3. Run migrations (after deployment):
```bash
railway run python -m alembic upgrade head
```

### If Using Render

1. Create PostgreSQL database in Render dashboard
2. Copy "Internal Database URL"
3. Add as `DATABASE_URL` environment variable in web service
4. Database will be empty - need to run schema creation

### Load Initial Schema

Connect to your production database and run:

```bash
# Get database URL from Railway/Render
export DATABASE_URL="postgresql://..."

# Run schema creation
psql $DATABASE_URL < database/schema/simplified_mvp_schema.sql
```

Or use Python:
```bash
railway run python
>>> from api.database import engine, Base
>>> Base.metadata.create_all(engine)
```

---

## 🧪 Testing Deployed Backend

Once deployed, test the API:

### 1. Health Check
```bash
curl https://your-api-url.com/health
# Expected: {"status":"healthy","version":"1.0.0"}
```

### 2. API Documentation
Visit: `https://your-api-url.com/docs`

### 3. Test Member Endpoint (requires auth)
```bash
curl https://your-api-url.com/v1/members
# Expected: {"detail":"Not authenticated"} (this is correct!)
```

---

## 🔗 Connecting Frontend to Backend

Once backend is deployed:

### 1. Get Backend URL
- Railway: `railway domain` or check dashboard
- Render: Check service dashboard (e.g., `vitanexus-api.onrender.com`)

### 2. Update Frontend Environment Variables

In Vercel dashboard for frontend:

**Settings → Environment Variables → Add:**

```
VITE_API_BASE_URL = https://your-api-url.com
VITE_API_VERSION = v1
```

### 3. Update CORS in Backend

Add frontend URL to backend environment variables:

```
CORS_ORIGINS = ["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]
```

### 4. Redeploy Frontend
```bash
cd frontend
vercel --prod
```

---

## 📊 Deployment Checklist

### Pre-Deployment
- [x] Create `requirements.txt`
- [x] Create `Procfile`
- [x] Create `runtime.txt`
- [x] Create platform configs (railway.json, render.yaml)
- [x] Create environment variable template

### Deployment
- [ ] Choose platform (Railway/Render)
- [ ] Create account and login
- [ ] Deploy backend service
- [ ] Add PostgreSQL database
- [ ] Set environment variables
- [ ] Load database schema
- [ ] Test health endpoint

### Post-Deployment
- [ ] Update frontend VITE_API_BASE_URL
- [ ] Update backend CORS_ORIGINS
- [ ] Test full-stack connection
- [ ] Create test members via API
- [ ] Verify wearable data endpoints

---

## 🎯 Estimated Deployment Time

- **Railway**: 5-10 minutes
- **Render**: 10-15 minutes
- **Vercel + Neon**: 15-20 minutes

---

## 💰 Cost Estimates

### Railway
- **Free Tier**: $5 credit/month
- **Estimated usage**: ~$5-10/month (Starter plan)
- **Includes**: API hosting + PostgreSQL

### Render
- **Free Tier**: $0/month
- **Limitations**: Services spin down after inactivity (30s cold start)
- **Includes**: API hosting + PostgreSQL (both free)

### Vercel + Neon (PostgreSQL)
- **Vercel**: $0 (Hobby plan)
- **Neon**: $0 (Free tier)
- **Total**: $0/month
- **Limitations**: Serverless cold starts, separate database setup

---

## 🐛 Common Issues

### Issue: Database connection error
**Solution**: Check DATABASE_URL format:
```
postgresql://user:password@host:5432/database?sslmode=require
```

### Issue: Module not found error
**Solution**: Ensure all dependencies in requirements.txt

### Issue: CORS error in frontend
**Solution**: Add frontend URL to CORS_ORIGINS environment variable

### Issue: 502 Bad Gateway
**Solution**: Check logs, ensure PORT environment variable is used:
```python
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

---

## 📞 Quick Deploy Commands

### Railway (Once logged in)
```bash
cd "/Users/somtonweke/Inversion Health/Vita"
railway init
railway add --plugin postgresql
railway up
railway domain
```

### Check Deployment Status
```bash
railway logs
```

### Get Environment Variables
```bash
railway variables
```

---

## 🎉 Ready to Deploy!

All files are configured. Just choose your platform and run the deployment commands above.

**Recommended**: Start with Render free tier to test, then upgrade to Railway for production.
