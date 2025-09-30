# VitaNexus Quick Start Guide

Get the entire system running locally in 15 minutes.

---

## Prerequisites (One-Time Setup)

```bash
# 1. Install Python 3.11+
python --version  # Should be 3.11 or higher

# 2. Install Node.js 18+
node --version  # Should be 18.0 or higher

# 3. Install PostgreSQL 15+
psql --version  # Should be 15.0 or higher

# 4. Install Redis
redis-server --version  # Should be 7.0 or higher
```

---

## 5-Minute Backend Setup

```bash
# Clone repo (if not already done)
cd "Inversion Health/Vita"

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (takes ~2 minutes)
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Edit .env with your local settings:
# - DATABASE_URL=postgresql://postgres:password@localhost:5432/vitanexus_dev
# - SECRET_KEY=your-secret-key-here
# - JWT_SECRET_KEY=your-jwt-secret-here

# Create database
createdb vitanexus_dev

# Load schema
psql vitanexus_dev < database/schemas/vitanexus_schema.sql

# Start Redis (in separate terminal)
redis-server

# Start API server
cd api
python main.py

# ✅ API running at http://localhost:8000
# ✅ Swagger docs at http://localhost:8000/docs
```

---

## 5-Minute Frontend Setup

```bash
# In new terminal
cd frontend

# Install dependencies (takes ~3 minutes)
npm install

# Start development server
npm run dev

# ✅ Portal running at http://localhost:3000
```

---

## Test the System (5 Minutes)

### 1. Test Health Scoring Engine

```bash
# In new terminal, from project root
source venv/bin/activate

# Run health scoring demo
python services/analytics/health_scoring/scoring_engine.py

# You should see:
# - Sample member data
# - Calculated health score (1-100)
# - Risk category
# - Predicted annual cost
# - Top risk factors
# - Recommended interventions
```

### 2. Test Financial Engine

```bash
# Run financial modeling demo
python services/financial/financial_engine.py

# You should see:
# - Risk pool metrics
# - Savings calculation
# - Member rebates
# - Intervention ROI analysis
# - Financial forecast
```

### 3. Test Incentive Optimizer

```bash
# Run incentive optimization demo
python services/incentives/incentive_optimizer.py

# You should see:
# - High-value member targets
# - Recommended behaviors
# - Optimal incentive amounts
# - Expected ROI per offer
# - Portfolio optimization results
```

### 4. Test Pilot Analytics

```bash
# Run pilot analytics demo
python pilot/pilot_analytics.py

# You should see comprehensive report with:
# - Unit economics (LTV:CAC, savings rate)
# - Health outcomes (risk score changes)
# - Engagement metrics
# - Cohort analysis
# - Validation status
```

### 5. Test API Endpoints

```bash
# Open browser to http://localhost:8000/docs

# Try these endpoints:
# 1. GET /health - Should return {"status": "healthy"}
# 2. GET /v1/members - Should return empty list (no data yet)
# 3. Create test member via POST /v1/members (use "Try it out" in Swagger)
```

### 6. Test Frontend

```bash
# Open browser to http://localhost:3000

# You should see:
# - Member dashboard (with mock data)
# - Health score display
# - Risk factors
# - Recommended interventions
# - Rebates section
```

---

## Common Issues & Solutions

### "Database connection failed"

```bash
# Check PostgreSQL is running
pg_isready

# If not running:
# Mac: brew services start postgresql
# Linux: sudo systemctl start postgresql
# Windows: Start PostgreSQL service in Services app

# Verify database exists
psql -l | grep vitanexus_dev

# If not, create it:
createdb vitanexus_dev
psql vitanexus_dev < database/schemas/vitanexus_schema.sql
```

### "Redis connection failed"

```bash
# Check Redis is running
redis-cli ping  # Should return "PONG"

# If not running:
# Mac: brew services start redis
# Linux: sudo systemctl start redis
# Windows: Run redis-server.exe

# Start Redis manually:
redis-server
```

### "Module not found" errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# If specific module missing:
pip install <module-name>
```

### "Port already in use"

```bash
# Kill process on port 8000 (API)
# Mac/Linux: lsof -ti:8000 | xargs kill -9
# Windows: netstat -ano | findstr :8000, then taskkill /PID <pid> /F

# Or use different port:
cd api
uvicorn main:app --port 8001
```

### Frontend won't start

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Use different port if 3000 is taken
npm run dev -- --port 3001
```

---

## Development Workflow

### Make changes to backend:

```bash
# API auto-reloads on file changes (--reload flag)
cd api
uvicorn main:app --reload

# Changes to scoring_engine.py, financial_engine.py, etc.
# can be tested immediately with:
python services/analytics/health_scoring/scoring_engine.py
```

### Make changes to frontend:

```bash
# Vite hot-reloads on file changes
cd frontend
npm run dev

# Edit files in src/pages/, src/components/, etc.
# Browser auto-refreshes
```

### Run tests:

```bash
# Backend tests (when implemented)
pytest tests/

# Frontend tests
cd frontend
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## What to Build Next

### Easy Wins (1-2 hours each):
1. **Add member creation form** in frontend
2. **Implement login/logout** flow
3. **Create health profile editor** page
4. **Add wearable connection** UI with OAuth redirect
5. **Build programs page** showing available interventions

### Medium Complexity (4-8 hours each):
1. **Implement actual database queries** (replace mock data)
2. **Add file upload** for documents (ID, insurance cards)
3. **Create admin dashboard** for care managers
4. **Build email notifications** (welcome, reminders, rebates)
5. **Implement search & filters** for member list

### Advanced Features (2-5 days each):
1. **Real-time wearable sync** background jobs
2. **Mobile app** (React Native)
3. **Chat support** (integrated with Intercom/Zendesk)
4. **Advanced analytics** dashboards (Datadog, Grafana)
5. **ML model training pipeline** (actual XGBoost/TensorFlow)

---

## Useful Commands Reference

### Backend

```bash
# Start API
cd api && uvicorn main:app --reload

# Run specific service
python services/analytics/health_scoring/scoring_engine.py
python services/financial/financial_engine.py
python services/incentives/incentive_optimizer.py
python pilot/pilot_analytics.py

# Database
psql vitanexus_dev  # Connect to DB
\dt                 # List tables
\d members          # Describe members table

# Redis
redis-cli           # Connect to Redis
KEYS *              # List all keys
GET key_name        # Get value
```

### Frontend

```bash
# Start dev server
cd frontend && npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run type-check

# Lint
npm run lint
```

### Testing

```bash
# API endpoint testing
curl http://localhost:8000/health
curl http://localhost:8000/v1/members

# Or use httpie (prettier output)
http http://localhost:8000/health

# Load testing
locust -f tests/load/locustfile.py --host http://localhost:8000
```

---

## Project Structure Quick Reference

```
api/
├── main.py              # FastAPI app entry point
├── config.py            # Settings (from .env)
├── database.py          # SQLAlchemy setup
├── dependencies/
│   └── auth.py          # JWT authentication
├── models/              # Pydantic request/response models
├── routers/             # API endpoints
└── services/            # Business logic

services/
├── analytics/health_scoring/
├── financial/
└── incentives/

frontend/
├── src/
│   ├── pages/           # React page components
│   ├── components/      # Reusable UI components
│   ├── services/        # API client
│   ├── types/           # TypeScript types
│   └── utils/           # Helper functions

database/
└── schemas/
    └── vitanexus_schema.sql  # PostgreSQL schema

pilot/
└── pilot_analytics.py   # Unit economics validation

ml/
└── model_iteration.py   # ML continuous improvement

infrastructure/
└── terraform/           # AWS deployment
```

---

## Environment Variables (.env)

**Minimum required for local development:**

```bash
# Application
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-change-in-prod
JWT_SECRET_KEY=your-jwt-secret-change-in-prod

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/vitanexus_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

**Full configuration:** See `.env.example`

---

## Next Steps

1. ✅ **Complete quick start** (you're here!)
2. 📖 **Read [ARCHITECTURE.md](ARCHITECTURE.md)** - Understand system design
3. 📖 **Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - See what's built
4. 🔨 **Build a feature** - Pick from "What to Build Next"
5. 🚀 **Deploy to staging** - Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## Getting Help

- **Documentation**: All markdown files in project root
- **API Docs**: http://localhost:8000/docs (when running)
- **Code Comments**: Extensive docstrings in all Python files
- **Type Hints**: Full TypeScript types in frontend/src/types/

---

**You're ready to start building! 🚀**

The entire VitaNexus platform is now running locally. Make changes, test features, and validate the business model that healthcare should reward wellness, not sickness.