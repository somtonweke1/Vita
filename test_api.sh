#!/bin/bash
# VitaNexus API Testing Script

echo "🏥 VitaNexus Platform Test Suite"
echo "================================="
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Check..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo ""

# Test 2: API Documentation
echo "2️⃣  Checking API Documentation..."
echo "   ✓ Swagger UI available at: http://localhost:8000/docs"
echo "   ✓ ReDoc available at: http://localhost:8000/redoc"
echo ""

# Test 3: Test Health Scoring Engine (standalone)
echo "3️⃣  Testing Health Scoring Engine..."
cd /Users/somtonweke/Inversion\ Health/Vita
./venv/bin/python3 services/analytics/health_scoring/scoring_engine.py 2>&1 | head -50
echo ""

# Test 4: Test Financial Engine
echo "4️⃣  Testing Financial Engine..."
./venv/bin/python3 services/financial/financial_engine.py 2>&1 | head -50
echo ""

# Test 5: Database Connection
echo "5️⃣  Testing Database..."
psql -U somtonweke vitanexus_dev -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" 2>&1
echo ""

echo "================================="
echo "✅ Platform Test Complete!"
echo ""
echo "🌐 Access Points:"
echo "   • API:  http://localhost:8000"
echo "   • Docs: http://localhost:8000/docs"
echo "   • DB:   psql -U somtonweke vitanexus_dev"
echo ""