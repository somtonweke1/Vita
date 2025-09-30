#!/bin/bash

# VitaNexus Deployment Script
# Automated deployment orchestration

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║         VitaNexus Deployment Script                                  ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Deployment mode (local, staging, production)
DEPLOY_MODE="${1:-local}"

echo "Deployment Mode: $DEPLOY_MODE"
echo ""

# Step 1: Check Prerequisites
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Checking Prerequisites"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python installed: $PYTHON_VERSION"
else
    print_error "Python 3.11+ is required"
    exit 1
fi

if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status "Node.js installed: $NODE_VERSION"
else
    print_error "Node.js 18+ is required"
    exit 1
fi

if [ "$DEPLOY_MODE" = "local" ]; then
    if command_exists psql; then
        print_status "PostgreSQL client installed"
    else
        print_warning "PostgreSQL client not found (optional for local dev)"
    fi

    if command_exists redis-cli; then
        print_status "Redis client installed"
    else
        print_warning "Redis client not found (optional for local dev)"
    fi
fi

if [ "$DEPLOY_MODE" != "local" ]; then
    if command_exists docker; then
        print_status "Docker installed"
    else
        print_error "Docker is required for non-local deployments"
        exit 1
    fi

    if command_exists terraform; then
        print_status "Terraform installed"
    else
        print_error "Terraform is required for cloud deployment"
        exit 1
    fi

    if command_exists kubectl; then
        print_status "kubectl installed"
    else
        print_error "kubectl is required for Kubernetes deployment"
        exit 1
    fi
fi

echo ""

# Step 2: Set up Environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Environment Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f .env ]; then
    print_warning ".env file not found, creating from example..."
    cp .env.example .env
    print_status "Created .env file - PLEASE EDIT WITH YOUR CREDENTIALS"
    echo ""
    echo "Edit .env and set:"
    echo "  - DATABASE_URL"
    echo "  - SECRET_KEY"
    echo "  - JWT_SECRET_KEY"
    echo ""
    read -p "Press Enter when .env is configured..."
else
    print_status ".env file exists"
fi

echo ""

# Step 3: Install Dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Installing Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Python virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

print_status "Activating virtual environment..."
source venv/bin/activate

print_status "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""

# Frontend dependencies (if deploying frontend)
if [ "$DEPLOY_MODE" = "local" ] || [ "$DEPLOY_MODE" = "staging" ]; then
    if [ -d "frontend" ]; then
        print_status "Installing frontend dependencies..."
        cd frontend
        npm install --silent
        cd ..
    fi
fi

echo ""

# Step 4: Database Setup (Local only)
if [ "$DEPLOY_MODE" = "local" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Step 4: Database Setup (Local)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if command_exists psql; then
        print_status "Checking PostgreSQL connection..."

        # Check if database exists
        if psql -lqt | cut -d \| -f 1 | grep -qw vitanexus_dev; then
            print_status "Database 'vitanexus_dev' exists"
        else
            print_warning "Database 'vitanexus_dev' not found"
            echo "To create database, run:"
            echo "  createdb vitanexus_dev"
            echo "  psql vitanexus_dev < database/schemas/vitanexus_schema.sql"
        fi
    else
        print_warning "PostgreSQL not installed - using Docker or remote database"
    fi

    echo ""
fi

# Step 5: Run Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Testing Core Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

print_status "Testing health scoring engine..."
python3 services/analytics/health_scoring/scoring_engine.py > /dev/null 2>&1 && print_status "Health scoring: OK" || print_error "Health scoring: FAILED"

print_status "Testing financial engine..."
python3 services/financial/financial_engine.py > /dev/null 2>&1 && print_status "Financial engine: OK" || print_error "Financial engine: FAILED"

print_status "Testing incentive optimizer..."
python3 services/incentives/incentive_optimizer.py > /dev/null 2>&1 && print_status "Incentive optimizer: OK" || print_error "Incentive optimizer: FAILED"

echo ""

# Step 6: Start Services
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 6: Starting Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$DEPLOY_MODE" = "local" ]; then
    print_status "Starting API server in background..."

    # Kill existing server if running
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true

    # Start API server in background
    cd api
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/api.log 2>&1 &
    API_PID=$!
    cd ..

    # Wait for API to start
    sleep 3

    # Test API health
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "API server started (PID: $API_PID)"
        print_status "API running at: http://localhost:8000"
        print_status "API docs at: http://localhost:8000/docs"
    else
        print_error "API server failed to start"
        echo "Check logs/api.log for errors"
    fi

    echo ""

    # Start frontend if exists
    if [ -d "frontend" ]; then
        print_status "Starting frontend in background..."

        # Kill existing frontend if running
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true

        cd frontend
        nohup npm run dev > ../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        cd ..

        sleep 3

        print_status "Frontend started (PID: $FRONTEND_PID)"
        print_status "Portal running at: http://localhost:3000"
    fi

elif [ "$DEPLOY_MODE" = "staging" ] || [ "$DEPLOY_MODE" = "production" ]; then

    # Build Docker images
    print_status "Building Docker images..."
    docker build -t vitanexus/api:latest .

    if [ -d "frontend" ]; then
        cd frontend
        docker build -t vitanexus/portal:latest .
        cd ..
    fi

    print_status "Docker images built successfully"

    echo ""
    echo "Next steps for $DEPLOY_MODE deployment:"
    echo "  1. Push images to container registry"
    echo "  2. Configure Terraform backend (infrastructure/terraform/)"
    echo "  3. Run: cd infrastructure/terraform && terraform apply"
    echo "  4. Deploy to Kubernetes: kubectl apply -f infrastructure/kubernetes/"
    echo ""
    echo "See DEPLOYMENT_GUIDE.md for detailed instructions"
fi

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Deployment Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$DEPLOY_MODE" = "local" ]; then
    echo ""
    echo "✓ VitaNexus deployed locally!"
    echo ""
    echo "Services:"
    echo "  • API:    http://localhost:8000"
    echo "  • Docs:   http://localhost:8000/docs"
    echo "  • Portal: http://localhost:3000"
    echo ""
    echo "Logs:"
    echo "  • API:      tail -f logs/api.log"
    echo "  • Frontend: tail -f logs/frontend.log"
    echo ""
    echo "To stop services:"
    echo "  kill $API_PID $FRONTEND_PID"
    echo ""
    echo "Quick tests:"
    echo "  curl http://localhost:8000/health"
    echo "  python3 pilot/pilot_analytics.py"
    echo ""
fi

echo "For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║  🚀 VitaNexus: Healthcare that rewards wellness, not sickness       ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"