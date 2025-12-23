#!/bin/bash

# Inbound Order MCP Server Startup Script

echo "🚀 Starting Inbound Order MCP Server..."
echo ""

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create contexts directories if they don't exist
mkdir -p contexts/gmail_profile
mkdir -p contexts/arcadia_profile

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting server on http://0.0.0.0:8080"
echo "MCP endpoint: http://0.0.0.0:8080/mcp"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

