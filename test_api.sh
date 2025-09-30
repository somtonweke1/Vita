#!/bin/bash
# VitaNexus API Testing Script
# Enhanced version with error handling, color output, and production support

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
DB_USER="${DB_USER:-somtonweke}"
DB_NAME="${DB_NAME:-vitanexus_dev}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_test() {
    echo -e "\n${YELLOW}▶ Test $1: $2${NC}"
    TESTS_RUN=$((TESTS_RUN + 1))
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_info() {
    echo -e "${BLUE}  ℹ $1${NC}"
}

# Main script
print_header "🏥 VitaNexus Platform Test Suite"
echo -e "${BLUE}Testing API at: ${API_URL}${NC}\n"

# Test 1: Health Check
print_test "1" "Health Check Endpoint"
if response=$(curl -s -w "%{http_code}" "${API_URL}/health"); then
    http_code="${response: -3}"
    body="${response:0:${#response}-3}"

    if [ "$http_code" = "200" ]; then
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
        print_success "Health check passed (HTTP $http_code)"
    else
        print_error "Health check failed (HTTP $http_code)"
        echo "$body"
    fi
else
    print_error "Could not connect to API at ${API_URL}"
    print_info "Make sure the API is running: uvicorn api.main:app --host 0.0.0.0 --port 8000"
fi

# Test 2: API Documentation
print_test "2" "API Documentation"
if curl -s -o /dev/null -w "%{http_code}" "${API_URL}/docs" | grep -q "200"; then
    print_success "Swagger UI available at: ${API_URL}/docs"
else
    print_error "Swagger UI not accessible"
fi

if curl -s -o /dev/null -w "%{http_code}" "${API_URL}/redoc" | grep -q "200"; then
    print_success "ReDoc available at: ${API_URL}/redoc"
else
    print_error "ReDoc not accessible"
fi

# Test 3: OpenAPI Spec
print_test "3" "OpenAPI Specification"
if curl -s "${API_URL}/v1/openapi.json" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    print_success "OpenAPI spec is valid JSON"
else
    print_error "OpenAPI spec is invalid or not available"
fi

# Test 4: Health Scoring Engine (if running locally)
if [ -f "${PROJECT_DIR}/venv/bin/python3" ]; then
    print_test "4" "Health Scoring Engine (Standalone)"
    if output=$("${PROJECT_DIR}/venv/bin/python3" "${PROJECT_DIR}/services/analytics/health_scoring/scoring_engine.py" 2>&1 | head -50); then
        echo "$output"
        if echo "$output" | grep -q "Overall Health Score"; then
            print_success "Health scoring engine working"
        else
            print_error "Health scoring engine output unexpected"
        fi
    else
        print_error "Health scoring engine failed"
    fi
else
    print_info "Skipping local Python tests (virtual environment not found)"
fi

# Test 5: Financial Engine (if running locally)
if [ -f "${PROJECT_DIR}/venv/bin/python3" ]; then
    print_test "5" "Financial Engine (70/30 Split)"
    if output=$("${PROJECT_DIR}/venv/bin/python3" "${PROJECT_DIR}/services/financial/financial_engine.py" 2>&1 | head -50); then
        echo "$output"
        if echo "$output" | grep -q "Company Profit"; then
            print_success "Financial engine working"
        else
            print_error "Financial engine output unexpected"
        fi
    else
        print_error "Financial engine failed"
    fi
else
    print_info "Skipping local Python tests (virtual environment not found)"
fi

# Test 6: Database Connection (if local)
if command -v psql &> /dev/null && [ "$API_URL" = "http://localhost:8000" ]; then
    print_test "6" "Database Connection"
    if tables=$(psql -U "$DB_USER" "$DB_NAME" -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null); then
        echo "$tables" | sed 's/^/  /'
        table_count=$(echo "$tables" | wc -l | tr -d ' ')
        print_success "Database connection successful ($table_count tables found)"

        # Check for required tables
        for table in members health_risk_scores wearable_metrics; do
            if echo "$tables" | grep -q "$table"; then
                print_success "Table '$table' exists"
            else
                print_error "Table '$table' missing"
            fi
        done
    else
        print_error "Could not connect to database"
    fi
else
    print_info "Skipping database tests (psql not available or not local)"
fi

# Test 7: API Endpoints (sample)
print_test "7" "API Endpoints"

# Test members endpoint (should require auth)
if response=$(curl -s -w "%{http_code}" "${API_URL}/v1/members"); then
    http_code="${response: -3}"
    if [ "$http_code" = "403" ] || [ "$http_code" = "401" ]; then
        print_success "Members endpoint requires authentication (HTTP $http_code)"
    elif [ "$http_code" = "200" ]; then
        print_success "Members endpoint accessible (HTTP $http_code)"
    else
        print_error "Members endpoint returned unexpected code (HTTP $http_code)"
    fi
fi

# Test 8: Environment Check
print_test "8" "Environment Configuration"
if [ -f "${PROJECT_DIR}/.env" ]; then
    print_success ".env file found"
else
    print_error ".env file not found"
    print_info "Copy .env.example to .env and configure"
fi

if [ -f "${PROJECT_DIR}/requirements.txt" ]; then
    print_success "requirements.txt found"
else
    print_error "requirements.txt not found"
fi

# Test 9: Test Data Check (if local)
if [ "$API_URL" = "http://localhost:8000" ] && command -v psql &> /dev/null; then
    print_test "9" "Test Data Check"
    if member_count=$(psql -U "$DB_USER" "$DB_NAME" -t -c "SELECT COUNT(*) FROM members;" 2>/dev/null | tr -d ' '); then
        if [ "$member_count" -gt 0 ]; then
            print_success "Found $member_count test members in database"
        else
            print_error "No test members found"
            print_info "Run: python create_test_members.py"
        fi
    fi

    if metric_count=$(psql -U "$DB_USER" "$DB_NAME" -t -c "SELECT COUNT(*) FROM wearable_metrics;" 2>/dev/null | tr -d ' '); then
        if [ "$metric_count" -gt 0 ]; then
            print_success "Found $metric_count wearable metrics in database"
        else
            print_error "No wearable metrics found"
            print_info "Run: python create_test_wearable_data.py"
        fi
    fi
fi

# Test 10: Frontend Check
print_test "10" "Frontend Status"
FRONTEND_URL="${FRONTEND_URL:-https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app}"
if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -q "200"; then
    print_success "Frontend accessible at: $FRONTEND_URL"
else
    print_error "Frontend not accessible at: $FRONTEND_URL"
fi

# Summary
echo ""
print_header "📊 Test Summary"
echo -e "${BLUE}Total Tests:  ${TESTS_RUN}${NC}"
echo -e "${GREEN}Passed:       ${TESTS_PASSED}${NC}"
echo -e "${RED}Failed:       ${TESTS_FAILED}${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}\n"
else
    echo -e "\n${RED}⚠️  Some tests failed!${NC}\n"
fi

# Access points summary
print_header "🌐 Access Points"
echo -e "${BLUE}API Server:${NC}    ${API_URL}"
echo -e "${BLUE}API Docs:${NC}      ${API_URL}/docs"
echo -e "${BLUE}Frontend:${NC}      ${FRONTEND_URL}"
if [ "$API_URL" = "http://localhost:8000" ]; then
    echo -e "${BLUE}Database:${NC}      psql -U ${DB_USER} ${DB_NAME}"
fi
echo ""

# Exit with appropriate code
if [ $TESTS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi