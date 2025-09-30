# Deploy VitaNexus - 100% FREE Options

**No credit card required!** 🎉

---

## 🆓 Best Free Option: Render

**Why Render?**
- ✅ **Completely FREE** (no credit card needed)
- ✅ **PostgreSQL included** (free tier)
- ✅ **Automatic HTTPS**
- ✅ **Auto-deploys from GitHub**
- ✅ **750 hours/month free** (enough for 24/7)

**Only limitation**: Services spin down after 15 min of inactivity (30-second cold start on next request)

---

## 🚀 Deploy to Render (5 Minutes)

### Step 1: Create Render Account
1. Go to: **https://render.com**
2. Click **"Get Started"**
3. Sign up with **GitHub** (free, no credit card)

### Step 2: Create PostgreSQL Database (FREE)

1. Click **"New +"** → **"PostgreSQL"**
2. Settings:
   - **Name**: `vitanexus-db`
   - **Database**: `vitanexus`
   - **User**: `vitanexus`
   - **Region**: `Oregon (US West)` (or closest to you)
   - **Plan**: **Free** ✅
3. Click **"Create Database"**
4. **Wait 2-3 minutes** for database to provision
5. **Copy "Internal Database URL"** (you'll need this)

### Step 3: Create Web Service (Backend)

1. Click **"New +"** → **"Web Service"**
2. **Connect your GitHub repository**:
   - Click **"Connect account"**
   - Authorize Render
   - Select: **`somtonweke1/Vita`**
3. Settings:
   - **Name**: `vitanexus-api`
   - **Region**: `Oregon (US West)` (same as database)
   - **Branch**: `main`
   - **Root Directory**: (leave blank)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free** ✅

### Step 4: Set Environment Variables

In the **Environment** section, add these variables:

```bash
# Database (paste from Step 2)
DATABASE_URL = [paste Internal Database URL from your PostgreSQL]

# Security (generate random strings)
SECRET_KEY = your-secret-key-here-change-this-to-random-string
JWT_SECRET_KEY = your-jwt-secret-key-here-change-this-to-random-string
PHI_ENCRYPTION_KEY = your-phi-encryption-key-here-change-this-to-random-string

# CORS (your Vercel frontend)
CORS_ORIGINS = ["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]

# Environment
ENVIRONMENT = production
DEBUG = false
ENABLE_API_DOCS = true
```

**Generate Secure Keys:**
```bash
# Run this locally to generate random keys
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('PHI_ENCRYPTION_KEY:', secrets.token_urlsafe(32))"
```

### Step 5: Deploy!

1. Click **"Create Web Service"**
2. **Wait 5-10 minutes** for first deploy
3. Watch the build logs (it will install dependencies and start)
4. Once you see "Deployed successfully", your backend is **LIVE**! ✅

### Step 6: Get Your Backend URL

Your URL will be something like:
```
https://vitanexus-api.onrender.com
```

Copy this URL!

---

## 🗄️ Load Database Schema

Once deployed, you need to load the database schema:

### Option 1: Via Render Shell (Easiest)

1. In Render dashboard, go to your **Web Service**
2. Click **"Shell"** tab (top right)
3. Run:
```bash
python -c "from api.database import Base, engine; Base.metadata.create_all(engine)"
```

### Option 2: Via Local psql

1. In Render dashboard, go to your **PostgreSQL database**
2. Copy the **"External Database URL"**
3. Run locally:
```bash
psql "postgresql://..." < database/schemas/vitanexus_simple_schema.sql
```

---

## 👥 Create Test Data

In Render Shell (or SSH):

```bash
python create_test_members.py
python create_test_wearable_data.py
```

Or via local connection:
```bash
# Set DATABASE_URL to your Render PostgreSQL
export DATABASE_URL="postgresql://..."
python create_test_members.py
python create_test_wearable_data.py
```

---

## 🔗 Connect Frontend to Backend

### Step 1: Update Vercel Environment Variables

1. Go to: https://vercel.com/somtonweke1s-projects/frontend/settings/environment-variables
2. Add new variable:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://vitanexus-api.onrender.com` (your Render URL)
   - **Environments**: Production, Preview, Development
3. Click **"Save"**

### Step 2: Redeploy Frontend

```bash
cd frontend
vercel --prod
```

Or in Vercel Dashboard:
1. Go to **"Deployments"** tab
2. Click **"..."** on latest deployment
3. Click **"Redeploy"**

---

## 🧪 Test Your Deployment

```bash
# Test backend health
curl https://vitanexus-api.onrender.com/health

# Test API docs
open https://vitanexus-api.onrender.com/docs

# Test frontend
open https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app
```

---

## 🎯 Alternative FREE Options

### Option 2: Fly.io (Also Free!)

**Free Tier:**
- 3 shared-cpu VMs (256MB RAM each)
- 3GB persistent storage
- 160GB outbound data transfer

**Deploy:**
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Deploy
cd "/Users/somtonweke/Inversion Health/Vita"
flyctl launch
```

### Option 3: PythonAnywhere (Free Tier)

**Free Tier:**
- 1 web app
- Limited CPU
- Good for testing

1. Go to: https://www.pythonanywhere.com
2. Create free account
3. Upload your code
4. Configure WSGI

### Option 4: Koyeb (Free Tier)

**Free Tier:**
- 1 web service
- 512 MB RAM
- No credit card required

1. Go to: https://www.koyeb.com
2. Sign up with GitHub
3. Deploy from repository

### Option 5: Cyclic.sh (Free Tier)

**Free Tier:**
- Unlimited apps
- Serverless functions
- Free PostgreSQL via Neon

1. Go to: https://cyclic.sh
2. Connect GitHub
3. Deploy

---

## 💰 Cost Comparison

| Platform | Free Tier | Limitations | Best For |
|----------|-----------|-------------|----------|
| **Render** ✅ | FREE | Cold starts after 15min | **Recommended** |
| **Fly.io** | FREE | 3 VMs, 256MB RAM each | Production-like |
| **PythonAnywhere** | FREE | Limited CPU | Testing |
| **Koyeb** | FREE | 1 service, 512MB RAM | Simple apps |
| **Railway** | $5/month | Pay as you go | When you have budget |

**Recommendation: Use Render (it's what I'll set up for you!)**

---

## 🐛 Render Troubleshooting

### Issue: Database connection error
**Solution**: Make sure `DATABASE_URL` uses the **Internal Database URL** from Render PostgreSQL dashboard

### Issue: Build failed
**Solution**: Check build logs. Make sure `requirements.txt` is in root directory

### Issue: Service won't start
**Solution**: Verify start command is: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Issue: Cold starts too slow
**Upgrade to paid tier ($7/month)** or **use Fly.io** (faster cold starts)

---

## 📊 Render Free Tier Limits

**What's Included (FREE):**
- ✅ 750 hours/month compute time
- ✅ 100 GB bandwidth/month
- ✅ PostgreSQL database (1GB storage)
- ✅ Automatic SSL/HTTPS
- ✅ Automatic deployments from GitHub
- ✅ Environment variables
- ✅ Custom domains (optional)

**Limitations:**
- ⚠️ Spins down after 15 min inactivity
- ⚠️ 30-second cold start when waking up
- ⚠️ 512 MB RAM (enough for this app)

**Perfect for:**
- ✅ MVPs and demos
- ✅ Personal projects
- ✅ Testing before production
- ✅ Low-traffic apps

---

## 🆙 When to Upgrade

**Stick with FREE if:**
- You're testing/demoing
- Low traffic (<100 requests/day)
- Don't mind 30-second cold starts
- No real-time requirements

**Upgrade to Paid ($7/month) if:**
- Need 24/7 uptime (no cold starts)
- Higher traffic (>1000 requests/day)
- Real-time features required
- Production app with users

---

## 🚀 Quick Deploy Script for Render

I'll create a helper script for you:

```bash
#!/bin/bash
# deploy_render.sh

echo "🚀 VitaNexus Render Deployment Helper"
echo ""
echo "1. Create account at: https://render.com"
echo "2. Create PostgreSQL database (FREE tier)"
echo "3. Copy the Internal Database URL"
echo ""
read -p "Paste your DATABASE_URL: " DATABASE_URL

echo ""
echo "Generating secure keys..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
PHI_ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo ""
echo "📋 Copy these environment variables to Render:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DATABASE_URL = $DATABASE_URL"
echo "SECRET_KEY = $SECRET_KEY"
echo "JWT_SECRET_KEY = $JWT_SECRET_KEY"
echo "PHI_ENCRYPTION_KEY = $PHI_ENCRYPTION_KEY"
echo 'CORS_ORIGINS = ["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]'
echo "ENVIRONMENT = production"
echo "DEBUG = false"
echo "ENABLE_API_DOCS = true"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "4. Create Web Service at: https://dashboard.render.com/select-repo"
echo "5. Paste the environment variables above"
echo "6. Build Command: pip install -r requirements.txt"
echo "7. Start Command: uvicorn api.main:app --host 0.0.0.0 --port \$PORT"
echo ""
```

---

## ✅ Deployment Checklist (Render)

- [ ] Create Render account (https://render.com)
- [ ] Create PostgreSQL database (FREE tier)
- [ ] Copy Internal Database URL
- [ ] Create Web Service (connect GitHub repo)
- [ ] Set environment variables (use script above)
- [ ] Wait for deployment (~5-10 min)
- [ ] Load database schema (via Shell)
- [ ] Create test data
- [ ] Update Vercel `VITE_API_BASE_URL`
- [ ] Redeploy frontend
- [ ] Test full-stack app

---

## 🎉 Result

**100% FREE full-stack deployment:**
- ✅ Frontend on Vercel (free)
- ✅ Backend on Render (free)
- ✅ PostgreSQL on Render (free)
- ✅ HTTPS everywhere
- ✅ Auto-deploys from GitHub

**Total Cost: $0/month** 🎉

---

## 📞 Quick Links

- **Render**: https://render.com
- **Render Docs**: https://render.com/docs
- **Your GitHub**: https://github.com/somtonweke1/Vita
- **Vercel Dashboard**: https://vercel.com/somtonweke1s-projects/frontend

---

**Deploy to Render now - it's 100% free and perfect for your needs!** 🚀
