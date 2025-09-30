#!/bin/bash
# VitaNexus Render Deployment Helper
# Generates secure keys and provides deployment instructions

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 VitaNexus - Render Deployment Helper (FREE)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This script will help you deploy VitaNexus to Render (100% FREE)"
echo ""

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

echo "Step 1: Create Render Account"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Go to: https://render.com"
echo "2. Click 'Get Started'"
echo "3. Sign up with GitHub (NO credit card required)"
echo ""
read -p "Press Enter when you've created your account..."
echo ""

echo "Step 2: Create PostgreSQL Database"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. In Render dashboard, click 'New +' → 'PostgreSQL'"
echo "2. Settings:"
echo "   - Name: vitanexus-db"
echo "   - Database: vitanexus"
echo "   - User: vitanexus"
echo "   - Region: Oregon (US West)"
echo "   - Plan: FREE ✅"
echo "3. Click 'Create Database'"
echo "4. Wait 2-3 minutes for provisioning"
echo "5. Copy the 'Internal Database URL'"
echo ""
read -p "Paste your DATABASE_URL here: " DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL is required"
    exit 1
fi

echo ""
echo "Step 3: Generating Secure Keys"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Generating random secure keys..."

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
PHI_ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo "✅ Keys generated successfully!"
echo ""

echo "Step 4: Create Web Service"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. In Render dashboard, click 'New +' → 'Web Service'"
echo "2. Connect your GitHub account"
echo "3. Select repository: somtonweke1/Vita"
echo "4. Settings:"
echo "   - Name: vitanexus-api"
echo "   - Region: Oregon (US West)"
echo "   - Branch: main"
echo "   - Runtime: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: uvicorn api.main:app --host 0.0.0.0 --port \$PORT"
echo "   - Plan: FREE ✅"
echo ""
read -p "Press Enter when you've configured the web service..."
echo ""

echo "Step 5: Environment Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Copy and paste these into Render's Environment section:"
echo ""
echo "DATABASE_URL"
echo "$DATABASE_URL"
echo ""
echo "SECRET_KEY"
echo "$SECRET_KEY"
echo ""
echo "JWT_SECRET_KEY"
echo "$JWT_SECRET_KEY"
echo ""
echo "PHI_ENCRYPTION_KEY"
echo "$PHI_ENCRYPTION_KEY"
echo ""
echo "CORS_ORIGINS"
echo '["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]'
echo ""
echo "ENVIRONMENT"
echo "production"
echo ""
echo "DEBUG"
echo "false"
echo ""
echo "ENABLE_API_DOCS"
echo "true"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save to file for reference
cat > render_env_vars.txt << EOF
# VitaNexus Render Environment Variables
# Generated: $(date)

DATABASE_URL=$DATABASE_URL
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
PHI_ENCRYPTION_KEY=$PHI_ENCRYPTION_KEY
CORS_ORIGINS=["https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"]
ENVIRONMENT=production
DEBUG=false
ENABLE_API_DOCS=true
EOF

echo "💾 Environment variables saved to: render_env_vars.txt"
echo ""

read -p "Press Enter after you've added all environment variables..."
echo ""

echo "Step 6: Deploy!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Click 'Create Web Service' in Render"
echo "2. Wait 5-10 minutes for deployment"
echo "3. Watch the build logs"
echo ""
read -p "Press Enter when deployment is complete..."
echo ""

echo "Step 7: Get Your Backend URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Paste your Render backend URL (e.g., https://vitanexus-api.onrender.com): " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  No URL provided. You can find it in Render dashboard."
    BACKEND_URL="https://vitanexus-api.onrender.com"
fi

echo ""
echo "Step 8: Load Database Schema"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "In Render dashboard:"
echo "1. Go to your Web Service (vitanexus-api)"
echo "2. Click 'Shell' tab"
echo "3. Run this command:"
echo ""
echo "   python -c \"from api.database import Base, engine; Base.metadata.create_all(engine)\""
echo ""
read -p "Press Enter after loading schema..."
echo ""

echo "Step 9: Create Test Data"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "In Render Shell, run:"
echo ""
echo "   python create_test_members.py"
echo "   python create_test_wearable_data.py"
echo ""
read -p "Press Enter after creating test data..."
echo ""

echo "Step 10: Update Frontend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Go to: https://vercel.com/somtonweke1s-projects/frontend/settings/environment-variables"
echo "2. Add new variable:"
echo "   - Name: VITE_API_BASE_URL"
echo "   - Value: $BACKEND_URL"
echo "3. Redeploy frontend:"
echo ""
echo "   cd frontend && vercel --prod"
echo ""
read -p "Press Enter after updating frontend..."
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your VitaNexus Platform is now LIVE! 🚀"
echo ""
echo "📍 Access Points:"
echo "   Backend:  $BACKEND_URL"
echo "   API Docs: $BACKEND_URL/docs"
echo "   Frontend: https://frontend-fghqf36ya-somtonweke1s-projects.vercel.app"
echo ""
echo "🧪 Test Your Deployment:"
echo "   curl $BACKEND_URL/health"
echo ""
echo "📊 Environment Variables saved to: render_env_vars.txt"
echo ""
echo "💡 Tip: Render free tier spins down after 15min of inactivity"
echo "    First request after sleep takes ~30 seconds (cold start)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Total Cost: \$0/month (100% FREE)"
echo ""
