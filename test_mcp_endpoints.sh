#!/bin/bash
# Test MCP server endpoints before connecting to Omni

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║               🧪 Testing MCP Server Endpoints                              ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

SERVER_URL="${1:-http://localhost:8080}"
echo "🌐 Testing server at: $SERVER_URL"
echo ""

# Test 1: Health check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s "$SERVER_URL/health")
if echo "$response" | grep -q "ok"; then
    echo "✅ Health check passed"
    echo "   Response: $response"
else
    echo "❌ Health check failed"
    echo "   Response: $response"
    exit 1
fi
echo ""

# Test 2: List tools
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: List Tools (REST endpoint)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s "$SERVER_URL/tools")
if echo "$response" | grep -q "extract_inbound_orders"; then
    echo "✅ Tools list endpoint working"
    tool_count=$(echo "$response" | grep -o '"name"' | wc -l)
    echo "   Found $tool_count tools"
else
    echo "❌ Tools list failed"
    exit 1
fi
echo ""

# Test 3: MCP Initialize
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: MCP Initialize (JSON-RPC)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s -X POST "$SERVER_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {},
    "id": 0
  }')
if echo "$response" | grep -q "serverInfo"; then
    echo "✅ MCP initialize successful"
    echo "   Server: $(echo "$response" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)"
else
    echo "❌ MCP initialize failed"
    echo "   Response: $response"
    exit 1
fi
echo ""

# Test 4: MCP Tools List
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4: MCP Tools/List (JSON-RPC)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s -X POST "$SERVER_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }')
if echo "$response" | grep -q "extract_inbound_orders"; then
    echo "✅ MCP tools/list successful"
    echo "   Available tools:"
    echo "$response" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | sed 's/^/      - /'
else
    echo "❌ MCP tools/list failed"
    exit 1
fi
echo ""

# Test 5: Root endpoint
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5: Root Endpoint Info"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s "$SERVER_URL/")
if echo "$response" | grep -q "service"; then
    echo "✅ Root endpoint accessible"
else
    echo "❌ Root endpoint failed"
    exit 1
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ ALL TESTS PASSED                                     ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Your MCP server is ready for Omni!"
echo ""
echo "📋 Next steps:"
echo "   1. Expose via ngrok: ngrok http 8080"
echo "   2. Get your ngrok URL (e.g., https://abc123.ngrok.io)"
echo "   3. Configure Omni to use: https://abc123.ngrok.io/mcp"
echo ""
echo "🔧 Available endpoints:"
echo "   • Health:    $SERVER_URL/health"
echo "   • Tools:     $SERVER_URL/tools"
echo "   • MCP:       $SERVER_URL/mcp (JSON-RPC 2.0)"
echo ""

