# Deploy VitaNexus from GitHub to Railway

Your code is now on GitHub: https://github.com/somtonweke1/Vita

## 🚀 One-Click Deploy to Railway

### Step 1: Open Railway and Connect GitHub

1. **Go to**: https://railway.app/new
2. **Click**: "Login" (top right)
3. **Sign in** with GitHub
4. **Authorize Railway** to access your repositories

### Step 2: Deploy from GitHub

1. **Click**: "Deploy from GitHub repo"
2. **Select**: `somtonweke1/Vita` from the list
3. Railway will automatically:
   - Detect it's a Python project
   - Read `railway.toml` configuration
   - Read `Procfile` for startup command
   - Install from `requirements.txt`
   - Start deploying!

### Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, **click**: "New" → "Database"
2. **Select**: "Add PostgreSQL"
3. Railway will automatically:
   - Create a PostgreSQL instance
   - Set `DATABASE_URL` environment variable
   - Connect it to your backend service

### Step 4: Set Environment Variables

1. Click on your **backend service** (vitanexus-api)
2. Go to **"Variables"** tab
3. **Add these variables**:

**Required Variables:**
```
SECRET_KEY = [click "Generate Random String"]
JWT_SECRET_KEY = [click "Generate Random String"]
PHI_ENCRYPTION_KEY = [click "Generate Random String"]
CORS_ORIGINS = ["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]
ENVIRONMENT = production
DEBUG = false
ENABLE_API_DOCS = true
```

**Note**: Railway has a "Generate" button for creating secure random strings!

### Step 5: Generate Public Domain

1. In your backend service, go to **"Settings"** tab
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. Copy your URL (e.g., `vitanexus-api.up.railway.app`)

### Step 6: Wait for Deployment

- **Build time**: ~2-3 minutes
- **Status**: Watch the "Deployments" tab
- **Logs**: Click "View Logs" to see progress

### Step 7: Verify Backend is Live

Once deployed, test your backend:

```bash
# Test health endpoint
curl https://your-app.up.railway.app/health

# Should return:
# {"status":"healthy","version":"1.0.0","environment":"production"}
```

**Open API docs:**
```
https://your-app.up.railway.app/docs
```

---

## 🗄️ Load Database Schema

Once backend is deployed:

### Option 1: Via Railway CLI

```bash
railway login
railway link  # Select your project
railway run python -c "from api.database import Base, engine; Base.metadata.create_all(engine)"
```

### Option 2: Via Railway Shell

1. In Railway dashboard, click your **PostgreSQL database**
2. Click **"Connect"** → **"psql"**
3. Copy the connection command and run locally:
```bash
psql postgresql://... < database/schemas/vitanexus_simple_schema.sql
```

### Option 3: Via Python (Easiest)

Railway Shell:
1. Click backend service → "Settings" → "Open Shell"
2. Run:
```python
python -c "from api.database import Base, engine; Base.metadata.create_all(engine)"
```

---

## 👥 Create Test Members

After database is set up:

```bash
# Via Railway CLI
railway run python create_test_members.py
railway run python create_test_wearable_data.py

# Or via Railway Shell (in dashboard)
python create_test_members.py
python create_test_wearable_data.py
```

---

## 🔗 Connect Frontend to Backend

### Step 1: Get Backend URL

From Railway dashboard, copy your backend URL:
```
https://vitanexus-api.up.railway.app
```

### Step 2: Update Vercel Frontend

1. Go to: https://vercel.com/somtonweke1s-projects/frontend/settings/environment-variables

2. **Add new environment variable**:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://vitanexus-api.up.railway.app` (your Railway URL)
   - **Environments**: Production, Preview, Development

3. **Click**: "Save"

### Step 3: Redeploy Frontend

```bash
cd frontend
vercel --prod
```

Or in Vercel dashboard:
1. Go to "Deployments" tab
2. Click "..." on latest deployment
3. Click "Redeploy"

---

## ✅ Test Full-Stack Application

### Test Backend
```bash
curl https://vitanexus-api.up.railway.app/health
```

### Test API Docs
```
https://vitanexus-api.up.railway.app/docs
```

### Test Frontend
```
https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app
```

**Expected**: Frontend should now load data from backend!

---

## 🎯 Complete Deployment Checklist

- [ ] Open Railway: https://railway.app/new
- [ ] Sign in with GitHub
- [ ] Deploy from GitHub repo: `somtonweke1/Vita`
- [ ] Add PostgreSQL database
- [ ] Set environment variables (SECRET_KEY, JWT_SECRET_KEY, etc.)
- [ ] Generate public domain
- [ ] Wait for deployment (~3 min)
- [ ] Test `/health` endpoint
- [ ] Load database schema
- [ ] Create test members
- [ ] Update Vercel `VITE_API_BASE_URL`
- [ ] Redeploy frontend
- [ ] Test full-stack app

---

## 💰 Railway Pricing

- **$5 free credit** per month
- **Usage-based pricing** after free tier
- **Estimated cost**: $5-10/month for this app
- Includes: Backend hosting + PostgreSQL + Bandwidth

---

## 🐛 Troubleshooting

### Deployment Failed?
**Check logs**: Railway dashboard → Deployments → View Logs

### Database Connection Error?
**Verify**: `DATABASE_URL` is automatically set by Railway when you add PostgreSQL

### CORS Error?
**Verify**: `CORS_ORIGINS` includes your Vercel frontend URL in the format:
```
["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]
```

### Environment Variable Not Working?
**Restart**: After adding variables, redeploy the service

---

## 📱 Quick Links

- **GitHub Repo**: https://github.com/somtonweke1/Vita
- **Railway Deploy**: https://railway.app/new
- **Vercel Frontend**: https://vercel.com/somtonweke1s-projects/frontend
- **Frontend URL**: https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app

---

## 🎉 You're Almost There!

**Total time**: 10 minutes
**Steps**: 7 simple clicks
**Result**: Full-stack app deployed! 🚀

**Start here**: https://railway.app/new

Once you see the Railway dashboard, everything is automated!
