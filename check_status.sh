#!/bin/bash

echo "═══════════════════════════════════════════════"
echo "  🔍 MCP SERVER STATUS CHECK"
echo "═══════════════════════════════════════════════"
echo ""

# Check if uvicorn is running
if ps aux | grep -v grep | grep "uvicorn.*8080" > /dev/null; then
    echo "✅ MCP Server: RUNNING on port 8080"
else
    echo "❌ MCP Server: NOT RUNNING"
fi

# Check if ngrok is running
if ps aux | grep -v grep | grep "ngrok.*8080" > /dev/null; then
    echo "✅ Ngrok: RUNNING"
    
    # Get ngrok URL
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'])" 2>/dev/null)
    
    if [ -n "$NGROK_URL" ]; then
        echo "   Public URL: $NGROK_URL"
        echo "   MCP Endpoint: $NGROK_URL/mcp"
    fi
else
    echo "❌ Ngrok: NOT RUNNING"
fi

echo ""
echo "─────────────────────────────────────────────────"
echo "  📡 Testing Local Server"
echo "─────────────────────────────────────────────────"

# Test local server
RESPONSE=$(curl -s http://localhost:8080/ 2>/dev/null)
if [ -n "$RESPONSE" ]; then
    echo "✅ Local server responding"
    echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'   Service: {data[\"service\"]}'); print(f'   Version: {data[\"version\"]}'); print(f'   Tools: {len(data[\"available_tools\"])}')" 2>/dev/null || echo "$RESPONSE"
else
    echo "❌ Local server not responding"
fi

echo ""
echo "─────────────────────────────────────────────────"
echo "  🔌 Testing MCP Tools Discovery"
echo "─────────────────────────────────────────────────"

# Test tools/list
TOOLS=$(curl -s -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' 2>/dev/null)

if [ -n "$TOOLS" ]; then
    echo "$TOOLS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'result' in data and 'tools' in data['result']:
    tools = data['result']['tools']
    print(f'✅ Found {len(tools)} tools:')
    for tool in tools:
        print(f'   • {tool[\"name\"]}')
else:
    print('❌ No tools found')
    print(json.dumps(data, indent=2))
" 2>/dev/null
else
    echo "❌ Could not retrieve tools"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "  📝 Add to Omni:"
echo "     Type: HTTP"
echo "     URL: $NGROK_URL/mcp"
echo "═══════════════════════════════════════════════"

