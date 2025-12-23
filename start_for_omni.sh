#!/bin/bash
# Quick start script for connecting to Omni

set -e

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║          🚀 Starting Inbound Order MCP Server for Omni                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if in correct directory
if [ ! -f "mcp/server.py" ]; then
    echo "❌ Error: Must run from inbound_mcp directory"
    echo "   cd to the directory containing mcp/server.py"
    exit 1
fi

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Check if MCP dependencies are installed
echo ""
echo "📦 Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "   ⚠️  FastAPI not installed. Installing MCP dependencies..."
    pip install -e .[mcp]
else
    echo "   ✅ Dependencies installed"
fi

# Check API key
echo ""
echo "🔑 Checking API key..."
if [ -z "$NOVA_ACT_API_KEY" ]; then
    echo "   ⚠️  NOVA_ACT_API_KEY not set"
    echo "   Set it with: export NOVA_ACT_API_KEY='your-key'"
    echo ""
    read -p "   Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "   ✅ API key is set"
fi

# Check port availability
echo ""
echo "🔌 Checking port 8080..."
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   ⚠️  Port 8080 is already in use"
    echo "   Kill the process with: lsof -ti:8080 | xargs kill -9"
    exit 1
else
    echo "   ✅ Port 8080 is available"
fi

# Start the server
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🌟 Starting MCP Server                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Server URL: http://localhost:8080"
echo "📍 Health check: http://localhost:8080/health"
echo "📍 MCP endpoint: http://localhost:8080/mcp"
echo ""
echo "🔧 To expose via ngrok (in another terminal):"
echo "   ngrok http 8080"
echo ""
echo "🌐 Then use the ngrok URL in Omni:"
echo "   https://your-id.ngrok.io/mcp"
echo ""
echo "⏸️  Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start uvicorn
uvicorn mcp.server:app --host 0.0.0.0 --port 8080

