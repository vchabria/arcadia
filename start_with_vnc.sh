#!/bin/bash
set -e

# Conditionally start VNC (only if ENABLE_VNC=true)
if [ "$ENABLE_VNC" = "true" ]; then
  echo "🖥️  VNC enabled - Starting VNC server..."
  ./start_vnc.sh &
  sleep 3
  echo "✅ VNC ready at:"
  echo "   - Direct VNC: vnc://your-server:5900"
  echo "   - Web VNC:    http://your-server:6080/vnc.html"
else
  echo "ℹ️  VNC disabled (set ENABLE_VNC=true to enable)"
fi

# Start the MCP server
echo "🚀 Starting MCP server on port ${PORT:-10000}..."
exec uvicorn mcp.server:app --host 0.0.0.0 --port ${PORT:-10000}
