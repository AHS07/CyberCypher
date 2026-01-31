#!/bin/bash
# Quick Start Script for Shadow Twin Guardian
# This starts both orchestrator and dashboard concurrently

set -e  # Exit on error

echo "🚀 Starting Shadow Twin Guardian..."
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing root dependencies..."
    npm install
fi

# Check orchestrator dependencies
if [ ! -d "orchestrator/venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    cd orchestrator
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Check dashboard dependencies
if [ ! -d "dashboard/node_modules" ]; then
    echo "📦 Installing dashboard dependencies..."
    cd dashboard
    npm install
    cd ..
fi

# Check environment files
if [ ! -f "orchestrator/.env" ]; then
    echo "⚠️  Warning: orchestrator/.env not found"
    echo "   Please copy .env.example and configure it"
    exit 1
fi

if [ ! -f "dashboard/.env.local" ]; then
    echo "⚠️  Warning: dashboard/.env.local not found"
    echo "   Please create it with NEXT_PUBLIC_* variables"
    exit 1
fi

echo "✅ All checks passed!"
echo ""
echo "Starting services..."
echo "  - Orchestrator: http://localhost:8000"
echo "  - Dashboard: http://localhost:3000"
echo ""

# Start both services
npm run dev
