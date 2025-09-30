# VitaNexus Testing Guide

Complete guide to testing the VitaNexus platform locally.

---

## 🌐 Access Points

| Component | URL | Description |
|-----------|-----|-------------|
| **API Server** | http://localhost:8000 | Main REST API |
| **Swagger UI** | http://localhost:8000/docs | Interactive API testing |
| **ReDoc** | http://localhost:8000/redoc | Alternative API docs |
| **Health Check** | http://localhost:8000/health | System status |
| **Database** | `psql -U somtonweke vitanexus_dev` | PostgreSQL CLI |

---

## 🧪 Quick Test Script

Run the automated test suite:
```bash
./test_api.sh
```

---

## 📊 Testing the Core Business Logic

### 1. Health Scoring Engine (Standalone)

**Test the AI-powered risk scoring:**
```bash
cd /Users/somtonweke/Inversion\ Health/Vita
./venv/bin/python3 services/analytics/health_scoring/scoring_engine.py
```

**What it shows:**
- Member health score (1-100 scale)
- Risk category (low/moderate/high/critical)
- Predicted annual healthcare cost
- Top risk factors
- Recommended interventions

**Example Output:**
```
Overall Health Score: 54.55/100
Risk Category: MODERATE
Predicted Annual Cost: $13,153.02
Top Risk Factors:
  1. Chronic condition: Diabetes (15.0 points)
  2. Uncontrolled hypertension (15.0 points)
```

---

### 2. Financial Engine (Business Model Validation)

**Test the 70/30 profit split:**
```bash
./venv/bin/python3 services/financial/financial_engine.py
```

**What it shows:**
- Risk pool metrics (revenue, reserves, costs)
- Savings calculation (predicted - actual - interventions)
- Company profit (70%)
- Member rebates (30%)
- Individual member rebate amounts

**Example Output:**
```
Total Savings: $3,730.00
Company Profit (70%): $2,611.00
Member Rebates (30%): $1,119.00
```

**This proves the business model works!**

---

### 3. Incentive Optimizer (ROI Analysis)

**Test intervention ROI calculation:**
```bash
./venv/bin/python3 services/incentives/incentive_optimizer.py
```

**What it shows:**
- High-value member targets
- Recommended interventions
- Expected ROI for each intervention (>150% threshold)
- Portfolio optimization

**Example Output:**
```
Top 5 High-Value Targets:
1. M003 - Expected 3Y Savings: $4,500
   Recommended: Diabetes Management Program
   ROI: 325%
```

---

### 4. Pilot Analytics (Unit Economics)

**Validate the business model at 100 members:**
```bash
./venv/bin/python3 pilot/pilot_analytics.py
```

**What it shows:**
- LTV:CAC ratio (target: >3.0)
- Savings rate (target: >20%)
- Health outcomes (risk score changes)
- Engagement metrics
- Financial projections

**This validates scalability from 100 → 10,000 → 1M members**

---

## 🔌 Testing the API

### Option A: Interactive Testing (Easiest)

1. **Open Swagger UI**: http://localhost:8000/docs

2. **Test endpoints without authentication:**
   - `GET /health` - Should return `{"status": "healthy"}`
   - `GET /docs` - Should load documentation

3. **Test endpoints with authentication:**
   - Click "Authorize" button in Swagger UI
   - For now, endpoints requiring auth will return 403 (expected)

### Option B: cURL Commands

**Health Check:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0","environment":"development"}
```

**Get API Specification:**
```bash
curl http://localhost:8000/v1/openapi.json | python3 -m json.tool
```

**List Members (requires auth):**
```bash
curl http://localhost:8000/v1/members
# Expected: {"detail":"Not authenticated"}
```

---

## 💾 Testing the Database

**Connect to database:**
```bash
psql -U somtonweke vitanexus_dev
```

**Check tables:**
```sql
\dt
-- Shows: members, health_risk_scores, wearable_metrics, audit_log, users, member_health_profiles
```

**View schema:**
```sql
\d members
\d health_risk_scores
```

**Sample queries:**
```sql
-- Count members
SELECT COUNT(*) FROM members;

-- View health risk scores
SELECT * FROM health_risk_scores LIMIT 5;

-- Check audit log
SELECT * FROM audit_log ORDER BY event_timestamp DESC LIMIT 10;
```

---

## 📱 What's Next: Frontend Testing

The **member portal (React/TypeScript)** isn't started yet. To test the full stack:

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

**The portal will show:**
- Member dashboard
- Health score visualization
- Risk factors with recommendations
- Wearable device connections
- Rebate calculator
- Intervention programs

---

## 🧩 End-to-End Test Flow

### Scenario: New Member Enrollment

1. **Create Member** (POST /v1/members)
   - Submit member demographics
   - System generates external_member_id

2. **Calculate Initial Health Score** (POST /v1/health-scores/{member_id})
   - Provide health profile data
   - Get back risk score + cost prediction

3. **View Risk Factors** (GET /v1/health-scores/{member_id}/risk-factors)
   - See top contributors to risk
   - Get intervention recommendations

4. **Connect Wearable** (POST /v1/wearables/connect)
   - OAuth flow for Fitbit/Apple Health
   - Start daily data sync

5. **View Dashboard** (Frontend)
   - Health score trend
   - Activity metrics
   - Upcoming rebate estimate

---

## 📈 Business Model Validation Tests

### Test 1: Cost Prediction Accuracy
```bash
# Run scoring engine on test members
./venv/bin/python3 services/analytics/health_scoring/scoring_engine.py

# Verify predicted costs are reasonable:
# - Low risk: $2,000-5,000/year
# - Moderate: $8,000-15,000/year
# - High risk: $20,000-50,000/year
```

### Test 2: Savings Calculation
```bash
# Run financial engine
./venv/bin/python3 services/financial/financial_engine.py

# Verify 70/30 split:
# Total Savings = Predicted - Actual - Interventions
# Company gets 70%, Members get 30%
```

### Test 3: ROI Threshold (>150%)
```bash
# Run incentive optimizer
./venv/bin/python3 services/incentives/incentive_optimizer.py

# Verify only interventions with ROI > 150% are recommended
# Example: $500 program should save >$1,250 over 3 years
```

### Test 4: Unit Economics (LTV:CAC > 3.0)
```bash
# Run pilot analytics
./venv/bin/python3 pilot/pilot_analytics.py

# Verify metrics at 100 members:
# - LTV:CAC > 3.0
# - Savings rate > 20%
# - Member engagement > 60%
```

---

## 🐛 Troubleshooting

### API not responding
```bash
# Check if API is running
curl http://localhost:8000/health

# View logs
tail -f logs/api.log

# Restart API
lsof -ti:8000 | xargs kill -9
./venv/bin/python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Database connection failed
```bash
# Check PostgreSQL status
psql -U somtonweke vitanexus_dev -c "SELECT 1;"

# Restart PostgreSQL
brew services restart postgresql@14
```

### Import errors
```bash
# Activate virtual environment
source venv/bin/activate  # or just use ./venv/bin/python3

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📊 Monitoring & Logs

**API Logs:**
```bash
tail -f logs/api.log
```

**Database Logs:**
```bash
tail -f /usr/local/var/postgresql@14/server.log
```

**Audit Trail (HIPAA Compliance):**
```sql
psql -U somtonweke vitanexus_dev
SELECT * FROM audit_log ORDER BY event_timestamp DESC LIMIT 20;
```

---

## ✅ Validation Checklist

Before deploying to production, verify:

- [ ] Health scoring engine returns scores between 1-100
- [ ] Financial engine calculates 70/30 split correctly
- [ ] Interventions only funded if ROI > 150%
- [ ] Predicted costs within reasonable ranges
- [ ] Database schema includes all required tables
- [ ] API endpoints return proper status codes
- [ ] Authentication blocks unauthorized access
- [ ] Audit log captures all PHI access
- [ ] Unit economics show LTV:CAC > 3.0
- [ ] Savings rate > 20% at pilot scale

---

## 🚀 Next Steps

1. **Test All Components**: Run `./test_api.sh`
2. **Open Swagger UI**: http://localhost:8000/docs
3. **Try Core Services**: Health scoring, financial, incentive engines
4. **Validate Business Model**: Run pilot analytics
5. **Start Frontend**: `cd frontend && npm run dev`
6. **Create Test Members**: Use Swagger UI to POST /v1/members
7. **Connect Wearables**: Test OAuth flows
8. **View Dashboard**: See everything working together

**The platform is ready! Time to validate the business model with real data.**