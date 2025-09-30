# Deploy VitaNexus Backend to Railway

**Quick Deploy**: Railway is the best option for this FastAPI backend (too large for Vercel serverless)

---

## 🚀 Deploy in 5 Commands

```bash
# 1. Login to Railway (opens browser)
railway login

# 2. Initialize project
cd "/Users/somtonweke/Inversion Health/Vita"
railway init

# 3. Add PostgreSQL database
railway add

# Select "PostgreSQL" from the list

# 4. Deploy the backend
railway up

# 5. Generate public URL
railway domain
```

**That's it!** Your backend will be live at `https://your-app.railway.app`

---

## 📋 Detailed Steps

### Step 1: Install Railway CLI (if needed)
```bash
# Already installed at: /Users/somtonweke/.nvm/versions/node/v18.20.8/bin/railway
railway --version
```

### Step 2: Login
```bash
railway login
```
This will open your browser for GitHub authentication.

### Step 3: Initialize Project
```bash
cd "/Users/somtonweke/Inversion Health/Vita"
railway init
```

You'll be asked:
- **Project name**: `vitanexus-api` (or your choice)
- **Start from scratch**: Yes

### Step 4: Add PostgreSQL
```bash
railway add
```

Select "PostgreSQL" from the menu. Railway will:
- Create a PostgreSQL database
- Set `DATABASE_URL` environment variable automatically
- Connect it to your service

### Step 5: Set Environment Variables

Railway will auto-generate some variables. Add these manually:

```bash
# Set via CLI
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set PHI_ENCRYPTION_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set CORS_ORIGINS='["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]'
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set ENABLE_API_DOCS=true
```

Or set via Railway dashboard (easier):
1. Go to https://railway.app/project/[your-project]/variables
2. Add:
   - `SECRET_KEY` = (generate random string)
   - `JWT_SECRET_KEY` = (generate random string)
   - `PHI_ENCRYPTION_KEY` = (generate random string)
   - `CORS_ORIGINS` = `["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]`
   - `ENVIRONMENT` = `production`
   - `DEBUG` = `false`

### Step 6: Deploy
```bash
railway up
```

Railway will:
- Detect Python project
- Install from `requirements.txt`
- Run command from `Procfile`
- Deploy to production

### Step 7: Get Your URL
```bash
railway domain
```

This generates a public URL like:
`https://vitanexus-api.railway.app`

---

## 🗄️ Load Database Schema

Once deployed, load your database schema:

```bash
# Option 1: Via Railway CLI
railway run psql < database/schema/simplified_mvp_schema.sql

# Option 2: Connect directly
railway connect postgres
# Then in psql:
\i database/schema/simplified_mvp_schema.sql
```

Or load via URL:
```bash
# Get database URL
railway variables | grep DATABASE_URL

# Connect and load
psql "postgresql://..." < database/schema/simplified_mvp_schema.sql
```

---

## 📊 Create Test Data

```bash
# Create test members
railway run python create_test_members.py

# Generate wearable data
railway run python create_test_wearable_data.py

# Validate business model
railway run python validate_business_model.py
```

---

## 🔗 Connect Frontend to Backend

### 1. Get Backend URL
```bash
railway domain
# Copy the URL (e.g., https://vitanexus-api.railway.app)
```

### 2. Update Frontend Environment Variables

```bash
cd frontend

# Update vercel.json to point to Railway backend
# Or set via Vercel dashboard
```

In Vercel Dashboard:
1. Go to: https://vercel.com/somtonweke1s-projects/frontend
2. Settings → Environment Variables
3. Add/Update:
   - `VITE_API_BASE_URL` = `https://vitanexus-api.railway.app`
   - `VITE_API_VERSION` = `v1`

### 3. Redeploy Frontend
```bash
cd frontend
vercel --prod
```

---

## 🧪 Test Your Deployment

### Test Backend Health
```bash
curl https://vitanexus-api.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-30T...",
  "version": "1.0.0",
  "environment": "production"
}
```

### Test API Docs
Open in browser:
```
https://vitanexus-api.railway.app/docs
```

### Test Frontend
```
https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app
```

Should now connect to Railway backend!

---

## 📈 Monitor Your Deployment

### View Logs
```bash
railway logs
```

### Check Status
```bash
railway status
```

### View in Dashboard
```bash
railway open
# Opens Railway dashboard in browser
```

---

## 💰 Pricing

Railway provides:
- **$5 free credits per month**
- **Pay-as-you-go** after free tier
- **Estimated cost**: $5-10/month for this app

**Included**:
- API hosting (automatic scaling)
- PostgreSQL database (500MB free)
- Automatic SSL/HTTPS
- Custom domains
- Monitoring & logs

---

## 🎯 Full Architecture After Deployment

```
Frontend (Vercel)
https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app
                    ↓
                  HTTPS
                    ↓
Backend (Railway)
https://vitanexus-api.railway.app
                    ↓
                  SQL
                    ↓
PostgreSQL (Railway)
[Automatically connected]
```

---

## 🔧 Troubleshooting

### Issue: Build fails
```bash
# Check logs
railway logs --build

# Ensure requirements.txt is complete
railway run pip install -r requirements.txt
```

### Issue: Database connection error
```bash
# Verify DATABASE_URL is set
railway variables | grep DATABASE_URL

# Test connection
railway run python -c "from api.database import check_db_connection; print(check_db_connection())"
```

### Issue: CORS errors
```bash
# Update CORS_ORIGINS to include frontend URL
railway variables set CORS_ORIGINS='["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]'
```

---

## ✅ Deployment Checklist

- [ ] `railway login` (opens browser)
- [ ] `railway init` (create project)
- [ ] `railway add` → Select PostgreSQL
- [ ] Set environment variables (SECRET_KEY, JWT_SECRET_KEY, etc.)
- [ ] `railway up` (deploy)
- [ ] `railway domain` (get URL)
- [ ] Load database schema
- [ ] Create test data
- [ ] Update frontend VITE_API_BASE_URL
- [ ] Redeploy frontend
- [ ] Test `/health` endpoint
- [ ] Test `/docs` endpoint
- [ ] Test frontend connection

---

## 🎉 Quick Copy-Paste Commands

```bash
# Complete deployment sequence
railway login
cd "/Users/somtonweke/Inversion Health/Vita"
railway init
railway add
# Select PostgreSQL
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set PHI_ENCRYPTION_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set CORS_ORIGINS='["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]'
railway variables set ENVIRONMENT=production
railway up
railway domain

# Load database
railway run psql < database/schema/simplified_mvp_schema.sql

# Create test data
railway run python create_test_members.py
railway run python create_test_wearable_data.py

# Test
curl $(railway domain)/health
```

---

**Total Time**: ~10 minutes
**Result**: Full-stack application deployed and running! 🚀
