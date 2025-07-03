#!/bin/bash

# AI-Powered Real Estate System - Quick Start Script
# This script helps you start all services quickly

echo "🚀 Starting AI-Powered Real Estate System..."
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not available. Please install Python 3.11+."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding."
    echo "   Required: BASEROW_TOKEN, BASEROW_APPLICATION_ID"
    exit 1
fi

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Test services
echo "🧪 Testing service health..."
python scripts/test_integration.py

echo ""
echo "✅ System startup complete!"
echo ""
echo "🌐 Access Points:"
echo "   - Web Dashboard: http://localhost:3000"
echo "   - n8n Workflows: http://localhost:5678"
echo "   - Lead Scoring API: http://localhost:5001"
echo "   - Property Search API: http://localhost:5002"
echo "   - Property Valuation API: http://localhost:5003"
echo "   - Email Marketing API: http://localhost:5004"
echo "   - Dashboard Analytics API: http://localhost:5005"
echo "   - Data Collection API: http://localhost:5006"
echo ""
echo "📚 Documentation:"
echo "   - Setup Guide: COMPLETE_SETUP_GUIDE.md"
echo "   - API Documentation: Available at each service /docs endpoint"
echo ""
echo "🎯 Next Steps:"
echo "1. Configure your Baserow tables: python setup_baserow_tables.py"
echo "2. Import n8n workflows from n8n/workflows/"
echo "3. Configure Open WebUI functions"
echo "4. Add real property data"
echo ""
