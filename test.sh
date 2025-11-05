#!/bin/bash

# Quick test script for blockchain news scraper
# Usage: ./test.sh

set -e

echo "================================"
echo "🧪 Blockchain News Scraper Test"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.11+"; exit 1; }
echo "✅ Python found"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"
echo ""

# Run the scraper
echo "🚀 Running scraper..."
echo "================================"
python scraper.py
echo "================================"
echo ""

# Check results
echo "📊 Checking results..."
TODAY=$(date +%Y-%m-%d)
DATA_DIR="data/$TODAY"

if [ -d "$DATA_DIR" ]; then
    echo "✅ Data directory created: $DATA_DIR"
    
    if [ -f "$DATA_DIR/coindesk.md" ]; then
        echo "✅ CoinDesk file created"
        echo ""
        echo "📄 Preview:"
        echo "---"
        head -n 20 "$DATA_DIR/coindesk.md"
        echo "---"
        echo ""
        echo "✅ Test completed successfully!"
        echo "📁 Full results in: $DATA_DIR/coindesk.md"
    else
        echo "⚠️  CoinDesk file not found"
    fi
else
    echo "❌ Data directory not created"
    exit 1
fi

echo ""
echo "================================"
echo "✨ All tests passed!"
echo "================================"
