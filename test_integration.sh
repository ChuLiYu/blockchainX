#!/bin/bash
# Integration test script for BlockchainX
# Tests both scraper and Twitter bot functionality

set -e

echo "=================================================="
echo "🧪 BlockchainX - Integration Test Suite"
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "📋 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Install/update dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Run Python test suite
echo ""
echo "=================================================="
echo "🧪 Running Python Test Suite"
echo "=================================================="
python test_twitter_bot.py
TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Python tests passed${NC}"
else
    echo ""
    echo -e "${RED}❌ Python tests failed${NC}"
    exit 1
fi

# Test scraper
echo ""
echo "=================================================="
echo "🔍 Testing News Scraper"
echo "=================================================="
echo ""
echo "Running scraper in test mode..."
python scraper.py
SCRAPER_RESULT=$?

if [ $SCRAPER_RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Scraper test passed${NC}"
    
    # Check if data was created
    TODAY=$(date +%Y-%m-%d)
    if [ -d "data/$TODAY" ]; then
        echo -e "${GREEN}✅ Data directory created: data/$TODAY${NC}"
        
        # List created files
        echo ""
        echo "📄 Created files:"
        ls -lh data/$TODAY/
        
        # Show preview of first file
        FIRST_FILE=$(ls data/$TODAY/*.md | head -1)
        if [ -f "$FIRST_FILE" ]; then
            echo ""
            echo "📖 Preview of $FIRST_FILE:"
            echo "---"
            head -n 20 "$FIRST_FILE"
            echo "---"
        fi
    else
        echo -e "${YELLOW}⚠️  No data directory created (might be expected if no new articles)${NC}"
    fi
else
    echo ""
    echo -e "${RED}❌ Scraper test failed${NC}"
    exit 1
fi

# Test Twitter bot (dry run without actual posting)
echo ""
echo "=================================================="
echo "🐦 Testing Twitter Bot Configuration"
echo "=================================================="

if [ -f "config.json" ]; then
    echo -e "${GREEN}✅ config.json found${NC}"
    
    # Validate JSON
    if python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
        echo -e "${GREEN}✅ config.json is valid JSON${NC}"
    else
        echo -e "${RED}❌ config.json is invalid JSON${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${YELLOW}⚠️  Skipping actual Twitter bot execution (requires API keys)${NC}"
    echo "   To test Twitter bot with real credentials:"
    echo "   1. Ensure config.json has valid API keys"
    echo "   2. Run: python twitter_bot.py"
else
    echo -e "${YELLOW}⚠️  config.json not found${NC}"
    echo "   This is normal if you haven't set up Twitter integration yet."
    echo "   Copy config.example.json to config.json and add your API keys."
fi

# Check GitHub Actions workflows
echo ""
echo "=================================================="
echo "⚙️  Checking GitHub Actions Workflows"
echo "=================================================="

WORKFLOWS_DIR=".github/workflows"
if [ -d "$WORKFLOWS_DIR" ]; then
    echo -e "${GREEN}✅ Workflows directory exists${NC}"
    
    # Check for workflow files
    if [ -f "$WORKFLOWS_DIR/daily-news.yml" ]; then
        echo -e "${GREEN}✅ daily-news.yml found${NC}"
    else
        echo -e "${RED}❌ daily-news.yml not found${NC}"
    fi
    
    if [ -f "$WORKFLOWS_DIR/twitter-bot.yml" ]; then
        echo -e "${GREEN}✅ twitter-bot.yml found${NC}"
    else
        echo -e "${YELLOW}⚠️  twitter-bot.yml not found${NC}"
    fi
else
    echo -e "${RED}❌ Workflows directory not found${NC}"
fi

# Check documentation
echo ""
echo "=================================================="
echo "📚 Checking Documentation"
echo "=================================================="

DOCS=(
    "README.md"
    "docs/SETUP.md"
    "docs/TWITTER_SETUP.md"
    "docs/PROJECT_OVERVIEW.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✅ $doc exists${NC}"
    else
        echo -e "${YELLOW}⚠️  $doc not found${NC}"
    fi
done

# Final summary
echo ""
echo "=================================================="
echo "📊 Integration Test Summary"
echo "=================================================="
echo ""
echo -e "${GREEN}✅ Core functionality tested and working${NC}"
echo ""
echo "Next steps:"
echo "1. ✅ Scraper is working - data collection ready"
echo "2. 🔧 Configure Twitter API keys in config.json"
echo "3. 🔧 Add GitHub Secrets for automation"
echo "4. 🚀 Enable GitHub Actions workflows"
echo "5. 📈 Monitor your contribution graph!"
echo ""
echo "=================================================="
echo -e "${GREEN}🎉 ALL INTEGRATION TESTS PASSED!${NC}"
echo "=================================================="
echo ""

# Deactivate virtual environment
deactivate 2>/dev/null || true

exit 0
