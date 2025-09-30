# VitaNexus Platform - Complete Map

**Last Updated**: September 30, 2025

---

## 🌐 Live Deployments

### Frontend (React/TypeScript)
- **URL**: https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app
- **Platform**: Vercel
- **Status**: ✅ LIVE
- **Dashboard**: https://vercel.com/somtonweke1s-projects/frontend
- **Source**: `frontend/` directory

### Backend (FastAPI/Python)
- **GitHub**: https://github.com/somtonweke1/Vita
- **Platform**: Ready for Railway/Render
- **Status**: ⏳ READY TO DEPLOY
- **Deploy Link**: https://railway.app/new
- **Source**: `api/` directory

### Database (PostgreSQL)
- **Local**: `vitanexus_dev` on localhost:5432
- **Production**: Auto-provision with Railway/Render
- **Status**: ⏳ Ready (will deploy with backend)
- **Schema**: `database/schemas/`

---

## 📂 Project Structure

### Root Directory: `/Users/somtonweke/Inversion Health/Vita`

```
VitaNexus/
│
├── 🎨 FRONTEND (React + TypeScript)
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx                 # Main app component
│       │   ├── main.tsx                # Entry point
│       │   ├── pages/
│       │   │   └── Dashboard.tsx       # Member dashboard
│       │   ├── services/
│       │   │   └── api.ts              # API client
│       │   ├── types/
│       │   │   └── member.ts           # TypeScript types
│       │   └── utils/
│       │       └── formatting.ts       # Utility functions
│       ├── package.json                # Dependencies
│       ├── vite.config.ts              # Build config
│       └── vercel.json                 # Deployment config
│
├── 🔧 BACKEND (FastAPI + Python)
│   └── api/
│       ├── main.py                     # FastAPI app entry
│       ├── config.py                   # Settings/environment
│       ├── database.py                 # DB connection
│       ├── models/
│       │   └── member.py               # SQLAlchemy models
│       ├── routers/
│       │   ├── members.py              # Member endpoints
│       │   ├── health_scores.py        # Health scoring endpoints
│       │   └── wearables.py            # Wearable endpoints
│       ├── dependencies/
│       │   └── auth.py                 # Authentication
│       └── services/
│           └── wearable_integrations.py # OAuth integrations
│
├── 💼 BUSINESS LOGIC
│   └── services/
│       ├── analytics/
│       │   └── health_scoring/
│       │       └── scoring_engine.py   # AI risk scoring
│       ├── financial/
│       │   └── financial_engine.py     # 70/30 profit split
│       └── incentives/
│           └── incentive_optimizer.py  # ROI calculations
│
├── 🗄️ DATABASE
│   └── database/
│       └── schemas/
│           ├── vitanexus_schema.sql    # Full schema
│           └── vitanexus_simple_schema.sql # MVP schema
│
├── 🧪 TESTING & DATA
│   ├── create_test_members.py          # Generate test members
│   ├── create_test_wearable_data.py    # Generate wearable data
│   ├── validate_business_model.py      # End-to-end validation
│   └── test_api.sh                     # Enhanced test suite
│
├── 📊 ANALYTICS
│   ├── pilot/
│   │   └── pilot_analytics.py          # Unit economics
│   └── ml/
│       └── model_iteration.py          # ML model training
│
├── 🔐 COMPLIANCE
│   └── compliance/
│       └── COMPLIANCE_FRAMEWORK.md     # HIPAA guidelines
│
├── 📚 DOCUMENTATION
│   ├── README.md                       # Project overview
│   ├── ARCHITECTURE.md                 # System architecture
│   ├── QUICKSTART.md                   # 15-min setup
│   ├── TESTING_GUIDE.md                # Testing instructions
│   ├── VALIDATION_RESULTS.md           # Business validation
│   │
│   ├── 🚀 DEPLOYMENT GUIDES
│   │   ├── FINAL_DEPLOYMENT_STATUS.md  # Current status ⭐
│   │   ├── GITHUB_DEPLOY_INSTRUCTIONS.md # Railway deploy ⭐
│   │   ├── COMPLETE_DEPLOYMENT_GUIDE.md # All options
│   │   ├── DEPLOY_TO_RAILWAY.md        # Railway specific
│   │   ├── BACKEND_DEPLOYMENT_GUIDE.md # Backend options
│   │   └── VERCEL_DEPLOYMENT.md        # Frontend details
│   │
│   └── 🧪 TESTING DOCS
│       ├── TEST_SCRIPT_README.md       # Test script usage
│       └── TEST_SCRIPT_IMPROVEMENTS.md # What's new
│
└── ⚙️ CONFIGURATION
    ├── requirements.txt                # Python dependencies
    ├── Procfile                        # Railway/Heroku startup
    ├── railway.toml                    # Railway config
    ├── railway.json                    # Railway settings
    ├── render.yaml                     # Render blueprint
    ├── runtime.txt                     # Python version
    ├── vercel.json                     # Vercel routing
    ├── .env.example                    # Environment template
    └── .gitignore                      # Git exclusions
```

---

## 🔑 Key Files & What They Do

### Frontend (React/TypeScript)
| File | Purpose | Location |
|------|---------|----------|
| `App.tsx` | Main application component | `frontend/src/` |
| `Dashboard.tsx` | Member dashboard UI | `frontend/src/pages/` |
| `api.ts` | API client for backend | `frontend/src/services/` |
| `vite.config.ts` | Build configuration | `frontend/` |
| `vercel.json` | Vercel deployment | `frontend/` |

### Backend (FastAPI/Python)
| File | Purpose | Location |
|------|---------|----------|
| `main.py` | FastAPI application | `api/` |
| `config.py` | Environment settings | `api/` |
| `database.py` | PostgreSQL connection | `api/` |
| `members.py` | Member CRUD endpoints | `api/routers/` |
| `health_scores.py` | Risk scoring API | `api/routers/` |

### Business Logic
| File | Purpose | Location |
|------|---------|----------|
| `scoring_engine.py` | AI-powered risk scoring | `services/analytics/health_scoring/` |
| `financial_engine.py` | 70/30 profit split | `services/financial/` |
| `incentive_optimizer.py` | ROI calculations | `services/incentives/` |
| `pilot_analytics.py` | Unit economics | `pilot/` |

### Testing & Validation
| File | Purpose | Location |
|------|---------|----------|
| `test_api.sh` | Enhanced test suite | Root |
| `create_test_members.py` | Generate test data | Root |
| `validate_business_model.py` | E2E validation | Root |

---

## 🌍 How to Access Each Part

### 1. Frontend (Live Now)
```bash
# Visit in browser
open https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app

# Or run locally
cd frontend
npm run dev
# Opens at http://localhost:3000
```

### 2. Backend (Local)
```bash
# Start API server
cd "/Users/somtonweke/Inversion Health/Vita"
./venv/bin/python3 -m uvicorn api.main:app --reload

# Access at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 3. Backend (Production - After Deploy)
```bash
# Will be at (after Railway deployment)
https://vitanexus-api.up.railway.app
```

### 4. Database (Local)
```bash
# Connect to PostgreSQL
psql -U somtonweke vitanexus_dev

# List tables
\dt

# View members
SELECT * FROM members;
```

### 5. Test Suite
```bash
# Run all tests
./test_api.sh

# Test production (after deploy)
API_URL=https://vitanexus-api.railway.app ./test_api.sh
```

### 6. Business Logic (Standalone)
```bash
# Health scoring
./venv/bin/python3 services/analytics/health_scoring/scoring_engine.py

# Financial engine
./venv/bin/python3 services/financial/financial_engine.py

# ROI optimizer
./venv/bin/python3 services/incentives/incentive_optimizer.py

# Unit economics
./venv/bin/python3 pilot/pilot_analytics.py
```

---

## 📊 Data Flow

```
User Browser
     │
     ▼
Frontend (Vercel) ✅
https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app
     │
     │ HTTPS + CORS
     ▼
Backend (Railway) ⏳
https://vitanexus-api.railway.app
     │
     ├─▶ Health Scoring Engine
     │   (services/analytics/health_scoring/)
     │
     ├─▶ Financial Engine
     │   (services/financial/)
     │
     ├─▶ Incentive Optimizer
     │   (services/incentives/)
     │
     └─▶ PostgreSQL Database
         (vitanexus_dev / vitanexus_prod)
```

---

## 🎯 Quick Commands Cheat Sheet

### Start Everything Locally
```bash
# 1. Start PostgreSQL (if not running)
brew services start postgresql@14

# 2. Start Backend API
cd "/Users/somtonweke/Inversion Health/Vita"
./venv/bin/python3 -m uvicorn api.main:app --reload

# 3. Start Frontend (separate terminal)
cd frontend
npm run dev
```

### Deploy Backend to Railway
```bash
# Login and deploy
railway login
cd "/Users/somtonweke/Inversion Health/Vita"
railway init
railway add  # Select PostgreSQL
railway up
railway domain
```

### Run Tests
```bash
# Local
./test_api.sh

# Production
API_URL=https://your-api.railway.app ./test_api.sh
```

### Create Test Data
```bash
./venv/bin/python3 create_test_members.py
./venv/bin/python3 create_test_wearable_data.py
./venv/bin/python3 validate_business_model.py
```

---

## 📍 Important Locations

### GitHub Repository
**https://github.com/somtonweke1/Vita**
- All source code
- Complete history
- Ready for deployment

### Vercel Dashboard
**https://vercel.com/somtonweke1s-projects/frontend**
- Frontend deployments
- Environment variables
- Analytics

### Railway (After Deploy)
**https://railway.app/dashboard**
- Backend service
- PostgreSQL database
- Environment variables
- Logs and monitoring

### Local Development
**`/Users/somtonweke/Inversion Health/Vita`**
- Complete codebase
- Virtual environment
- Local database
- Test data

---

## 📚 Essential Documentation

| What You Need | Read This | Location |
|---------------|-----------|----------|
| **Start Here** | README.md | Root |
| **Quick Setup** | QUICKSTART.md | Root |
| **Deploy Backend** | GITHUB_DEPLOY_INSTRUCTIONS.md ⭐ | Root |
| **Current Status** | FINAL_DEPLOYMENT_STATUS.md ⭐ | Root |
| **Test Platform** | TEST_SCRIPT_README.md | Root |
| **Validate Business** | VALIDATION_RESULTS.md | Root |
| **Architecture** | ARCHITECTURE.md | Root |
| **All Deploy Options** | COMPLETE_DEPLOYMENT_GUIDE.md | Root |

---

## 🎯 Current Status Summary

| Component | Status | Location |
|-----------|--------|----------|
| **Frontend** | ✅ DEPLOYED | https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app |
| **Backend Code** | ✅ ON GITHUB | https://github.com/somtonweke1/Vita |
| **Backend Deploy** | ⏳ READY | https://railway.app/new |
| **Local API** | ✅ RUNNING | http://localhost:8000 |
| **Local DB** | ✅ RUNNING | vitanexus_dev |
| **Test Data** | ✅ CREATED | 5 members, 150 metrics |
| **Documentation** | ✅ COMPLETE | 15+ guides |

---

## 🚀 Next Steps

1. **Deploy Backend** (5 minutes)
   ```bash
   railway login
   cd "/Users/somtonweke/Inversion Health/Vita"
   railway init && railway add && railway up
   ```

2. **Update Frontend** (2 minutes)
   - Add `VITE_API_BASE_URL` to Vercel
   - Redeploy: `vercel --prod`

3. **Test Everything** (1 minute)
   ```bash
   API_URL=https://your-api.railway.app ./test_api.sh
   ```

---

## 📞 Quick Access

**Everything is in one place:**
```
📁 /Users/somtonweke/Inversion Health/Vita/
```

**Or on GitHub:**
```
🌐 https://github.com/somtonweke1/Vita
```

**Or deployed (frontend):**
```
🌍 https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app
```

---

**Your complete VitaNexus platform is 95% deployed and ready for production!** 🎉
