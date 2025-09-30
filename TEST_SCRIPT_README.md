# VitaNexus Test Script Documentation

## Overview

The `test_api.sh` script is an enhanced testing suite for the VitaNexus platform with:
- ✅ Color-coded output for better readability
- ✅ Error handling and proper exit codes
- ✅ Support for both local and production environments
- ✅ Comprehensive test coverage (10 test suites)
- ✅ Automatic pass/fail tracking
- ✅ Configurable via environment variables

---

## Quick Start

### Test Local Environment
```bash
./test_api.sh
```

### Test Production/Railway
```bash
API_URL=https://vitanexus-api.up.railway.app ./test_api.sh
```

### Test with Custom Configuration
```bash
API_URL=https://your-api.com \
FRONTEND_URL=https://your-frontend.com \
DB_USER=postgres \
DB_NAME=vitanexus \
./test_api.sh
```

---

## What It Tests

### 1. **Health Check Endpoint** ✓
- Tests `/health` endpoint
- Validates HTTP 200 response
- Checks JSON response format
- **Pass**: API responds with healthy status
- **Fail**: API not responding or unhealthy

### 2. **API Documentation** ✓
- Tests `/docs` (Swagger UI)
- Tests `/redoc` (ReDoc)
- **Pass**: Documentation accessible
- **Fail**: Documentation endpoints not found

### 3. **OpenAPI Specification** ✓
- Tests `/v1/openapi.json`
- Validates JSON format
- **Pass**: Valid OpenAPI spec
- **Fail**: Invalid or missing spec

### 4. **Health Scoring Engine** ✓ (Local only)
- Runs standalone health scoring test
- Validates risk score calculation
- **Pass**: Engine produces expected output
- **Fail**: Engine errors or unexpected output

### 5. **Financial Engine** ✓ (Local only)
- Tests 70/30 profit split calculation
- Validates financial model
- **Pass**: Correct profit/rebate calculations
- **Fail**: Financial logic errors

### 6. **Database Connection** ✓ (Local only)
- Tests PostgreSQL connectivity
- Lists all tables
- Validates required tables exist
- **Pass**: Database connected, tables present
- **Fail**: Connection error or missing tables

### 7. **API Endpoints** ✓
- Tests protected endpoints
- Validates authentication
- **Pass**: Endpoints require proper auth
- **Fail**: Unexpected response codes

### 8. **Environment Configuration** ✓
- Checks for `.env` file
- Validates `requirements.txt`
- **Pass**: Config files present
- **Fail**: Missing configuration

### 9. **Test Data Check** ✓ (Local only)
- Counts test members
- Counts wearable metrics
- **Pass**: Test data exists
- **Fail**: No test data found

### 10. **Frontend Status** ✓
- Tests frontend accessibility
- **Pass**: Frontend loads successfully
- **Fail**: Frontend unreachable

---

## Environment Variables

### API Configuration
```bash
# API URL (default: http://localhost:8000)
API_URL=https://your-api-url.com

# Frontend URL (default: Vercel deployment)
FRONTEND_URL=https://your-frontend-url.com
```

### Database Configuration (Local only)
```bash
# Database user (default: somtonweke)
DB_USER=postgres

# Database name (default: vitanexus_dev)
DB_NAME=vitanexus_prod
```

---

## Color Output

The script uses color-coded output for clarity:

- 🔵 **Blue**: Headers and info messages
- 🟡 **Yellow**: Test names
- 🟢 **Green**: Success messages (✓)
- 🔴 **Red**: Error messages (✗)

### Disable Colors (CI/CD)
```bash
# Colors auto-disable if output is not a terminal
./test_api.sh | tee test-results.txt
```

---

## Exit Codes

- **0**: All tests passed ✅
- **1**: One or more tests failed ❌

Use in CI/CD:
```bash
#!/bin/bash
if ./test_api.sh; then
    echo "Deploy to production"
else
    echo "Tests failed, blocking deployment"
    exit 1
fi
```

---

## Example Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🏥 VitaNexus Platform Test Suite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Testing API at: http://localhost:8000

▶ Test 1: Health Check Endpoint
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
✓ Health check passed (HTTP 200)

▶ Test 2: API Documentation
✓ Swagger UI available at: http://localhost:8000/docs
✓ ReDoc available at: http://localhost:8000/redoc

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Tests:  20
Passed:       18
Failed:       2

⚠️  Some tests failed!
```

---

## Integration with CI/CD

### GitHub Actions
```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          chmod +x test_api.sh
          API_URL=${{ secrets.API_URL }} ./test_api.sh
```

### Railway/Render
```bash
# In deploy hook
./test_api.sh || exit 1
```

---

## Troubleshooting

### "Could not connect to API"
**Solution**: Make sure API is running
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### "Database connection failed"
**Solution**: Check PostgreSQL is running
```bash
psql -U somtonweke vitanexus_dev -c "SELECT 1;"
```

### "No test members found"
**Solution**: Create test data
```bash
python create_test_members.py
python create_test_wearable_data.py
```

### "Permission denied"
**Solution**: Make script executable
```bash
chmod +x test_api.sh
```

---

## Advanced Usage

### Test Only API (skip local tests)
```bash
# Set API_URL to production to skip venv checks
API_URL=https://your-api.railway.app ./test_api.sh
```

### Test with Verbose Output
```bash
# Add debug output
set -x
./test_api.sh
```

### Save Results to File
```bash
./test_api.sh 2>&1 | tee test-results-$(date +%Y%m%d).txt
```

### Run Specific Test Section
Extract individual tests from the script:
```bash
# Just health check
curl -s http://localhost:8000/health | python3 -m json.tool
```

---

## Continuous Testing

### Watch Mode (requires `entr`)
```bash
# Re-run tests on file changes
ls api/**/*.py | entr ./test_api.sh
```

### Scheduled Testing (cron)
```bash
# Add to crontab
*/15 * * * * cd /path/to/vita && ./test_api.sh >> logs/tests.log 2>&1
```

---

## Improvements from Original

### Original Script
- ❌ No error handling
- ❌ Hard-coded paths
- ❌ No pass/fail tracking
- ❌ Limited test coverage
- ❌ No color output
- ❌ No production support

### Enhanced Script
- ✅ Comprehensive error handling
- ✅ Environment variable configuration
- ✅ Test result tracking
- ✅ 10 test suites
- ✅ Color-coded output
- ✅ Local and production support
- ✅ Proper exit codes
- ✅ Frontend testing
- ✅ Test data validation
- ✅ CI/CD ready

---

## Contributing

To add new tests:

1. Add test function:
```bash
print_test "11" "Your Test Name"
if your_test_command; then
    print_success "Test passed"
else
    print_error "Test failed"
fi
```

2. Update test count automatically (handled by functions)

3. Document in this README

---

## Related Files

- `test_api.sh` - Main test script
- `create_test_members.py` - Generate test members
- `create_test_wearable_data.py` - Generate wearable data
- `validate_business_model.py` - Business model validation
- `.env.example` - Environment variable template

---

## Quick Reference

```bash
# Local testing
./test_api.sh

# Production testing
API_URL=https://api.railway.app ./test_api.sh

# Custom config
API_URL=https://api.com FRONTEND_URL=https://app.com ./test_api.sh

# Save results
./test_api.sh | tee results.txt

# CI/CD
./test_api.sh && deploy.sh
```

---

**The enhanced test script provides comprehensive validation of your entire VitaNexus platform!** 🚀
