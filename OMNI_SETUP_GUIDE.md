# 🌐 Connecting Refactored SDK to Omni

## Overview

The refactored architecture provides **two ways** to use the tool:

1. **Python SDK** (Direct) - For scripts, notebooks, CI/CD
2. **MCP Server** (For Omni) - HTTP endpoint for Omni integration ✅

To connect to Omni, you'll use the **MCP server layer** (the thin adapter).

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Install with MCP Support

```bash
cd inbound_mcp
pip install .[mcp]
```

This installs:
- Core SDK (pydantic)
- FastAPI, uvicorn (for MCP server)
- SSE support (for streaming)

---

### Step 2: Start the MCP Server

```bash
# Set your API key
export NOVA_ACT_API_KEY="your-api-key"

# Start the server
uvicorn mcp.server:app --host 0.0.0.0 --port 8080

# Server will start at http://localhost:8080
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

---

### Step 3: Expose via ngrok (For Remote Omni Access)

```bash
# In a new terminal
ngrok http 8080
```

You'll get a URL like:
```
https://abc123.ngrok.io
```

---

## 🔧 Configure in Omni

### Option A: Omni UI Configuration

1. Open Omni settings/integrations
2. Add new MCP server
3. Enter your URL: `https://abc123.ngrok.io/mcp`
4. Protocol: JSON-RPC 2.0
5. Save and test connection

### Option B: Omni Configuration File

If Omni uses a config file, add:

```json
{
  "mcpServers": {
    "inbound-orders": {
      "url": "https://abc123.ngrok.io/mcp",
      "name": "Inbound Order Automation",
      "description": "Automate Gmail-to-Arcadia order processing"
    }
  }
}
```

---

## 🧪 Test the Connection

### Test 1: Health Check

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "inbound_mcp"
}
```

### Test 2: List Tools

```bash
curl http://localhost:8080/tools
```

Expected response:
```json
{
  "tools": [
    {
      "name": "extract_inbound_orders",
      "description": "Extract inbound order data from Gmail..."
    },
    {
      "name": "add_to_arcadia",
      "description": "Submit extracted inbound orders to Arcadia..."
    },
    {
      "name": "create_arcadia_order",
      "description": "Create a single inbound order in Arcadia..."
    },
    {
      "name": "run_full_pipeline",
      "description": "Execute the complete automation pipeline..."
    }
  ]
}
```

### Test 3: MCP Initialize

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {},
    "id": 0
  }'
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2025-03-26",
    "serverInfo": {
      "name": "Inbound Order MCP",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {}
    }
  },
  "id": 0
}
```

### Test 4: Call a Tool

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_arcadia_order",
      "arguments": {
        "master_bill_number": "123456789",
        "product_code": "PP48F",
        "quantity": 24,
        "temperature": "FREEZER"
      }
    },
    "id": 1
  }'
```

---

## 📋 Available Tools in Omni

Once connected, Omni will have access to these 4 tools:

### 1. extract_inbound_orders

**Description:** Extract inbound orders from Gmail

**Arguments:** None

**Example in Omni:**
```
"Extract orders from the latest Inbound ATL email"
```

---

### 2. create_arcadia_order

**Description:** Create a single inbound order in Arcadia

**Arguments:**
- `master_bill_number` (string, required) - 9-digit master bill
- `product_code` (string, required) - Product SKU
- `quantity` (integer, required) - Number of pallets
- `temperature` (string, required) - FREEZER, COOLER, or FREEZER CRATES
- `delivery_date` (string, optional) - MM/DD/YYYY format
- `delivery_company` (string, optional) - Carrier code
- `comments` (string, optional) - Additional notes

**Example in Omni:**
```
"Create an order for master bill 123456789, product PP48F, 
24 pallets at FREEZER temperature, deliver on 12/25/2025 via FedEx"
```

---

### 3. add_to_arcadia

**Description:** Submit multiple extracted orders to Arcadia

**Arguments:**
- `order_data` (object, required) - Contains `email_subject` and `orders` array

**Example in Omni:**
```
"Submit the extracted orders to Arcadia"
```

---

### 4. run_full_pipeline

**Description:** Run complete pipeline (extract from Gmail + submit to Arcadia)

**Arguments:** None

**Example in Omni:**
```
"Run the full order automation pipeline"
```

---

## 🔐 Environment Variables

Make sure these are set before starting the server:

```bash
# Required
export NOVA_ACT_API_KEY="your-api-key"

# Optional (for custom Python path)
export PYTHON_PATH="/usr/local/bin/python3"
```

---

## 🚦 Server Management

### Start Server in Background

```bash
# Start in background
uvicorn mcp.server:app --host 0.0.0.0 --port 8080 &

# Get process ID
echo $! > server.pid

# Check if running
ps aux | grep uvicorn
```

### Stop Server

```bash
# If you saved the PID
kill $(cat server.pid)

# Or find and kill
pkill -f "uvicorn mcp.server:app"
```

### Auto-restart Server

Create a systemd service (Linux) or launchd (macOS):

**systemd (Linux):**
```ini
[Unit]
Description=Inbound Order MCP Server
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/inbound_mcp
Environment="NOVA_ACT_API_KEY=your-key"
ExecStart=/usr/local/bin/uvicorn mcp.server:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📊 Monitor the Server

### View Logs

```bash
# If running in foreground, logs appear in terminal

# If running in background, redirect to file
uvicorn mcp.server:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &

# Then tail the log
tail -f server.log
```

### Health Check Script

```bash
#!/bin/bash
# check_server.sh

HEALTH_URL="http://localhost:8080/health"

if curl -s $HEALTH_URL | grep -q "ok"; then
    echo "✅ Server is healthy"
    exit 0
else
    echo "❌ Server is down"
    exit 1
fi
```

---

## 🌐 Production Deployment

### Option 1: ngrok (Development/Testing)

```bash
# Start server
uvicorn mcp.server:app --host 0.0.0.0 --port 8080 &

# Expose via ngrok
ngrok http 8080

# Use the HTTPS URL in Omni
# Example: https://abc123.ngrok.io/mcp
```

**Pros:** Quick, easy, HTTPS included  
**Cons:** URL changes on restart, limited free tier

---

### Option 2: Cloud Deployment (Production)

**Deploy to Cloud:**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install .[mcp]

EXPOSE 8080

CMD ["uvicorn", "mcp.server:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Deploy to:**
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Heroku
- Railway.app
- Render.com

Then use the cloud URL in Omni.

---

### Option 3: Reverse Proxy (Advanced)

**nginx config:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /mcp {
        proxy_pass http://localhost:8080/mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
    }
}
```

---

## 🐛 Troubleshooting

### Server Won't Start

**Error:** `Address already in use`

```bash
# Check what's using port 8080
lsof -ti:8080

# Kill the process
kill -9 $(lsof -ti:8080)

# Or use a different port
uvicorn mcp.server:app --host 0.0.0.0 --port 8081
```

---

### Omni Can't Connect

**Check 1:** Server is running
```bash
curl http://localhost:8080/health
```

**Check 2:** ngrok is exposing correctly
```bash
curl https://your-ngrok-url.ngrok.io/health
```

**Check 3:** Firewall allows port 8080
```bash
# Linux
sudo ufw allow 8080

# macOS
# System Preferences → Security & Privacy → Firewall
```

---

### Tool Calls Fail

**Check 1:** API key is set
```bash
echo $NOVA_ACT_API_KEY
```

**Check 2:** Scripts exist
```bash
ls ../stagehand-test/extraction_only.py
ls ../stagehand-test/run_arcadia_only.py
```

**Check 3:** Server logs for errors
```bash
# Check server output for detailed error messages
tail -f server.log
```

---

## 📱 Omni Usage Examples

Once connected, you can use natural language in Omni:

### Example 1: Extract Orders
```
"Check the latest Inbound ATL email and extract the orders"
```

Omni will call: `extract_inbound_orders`

---

### Example 2: Create Single Order
```
"Create an inbound order for master bill 123456789, 
product PP48F, 24 pallets, freezer temperature"
```

Omni will call: `create_arcadia_order` with parameters

---

### Example 3: Full Pipeline
```
"Process all new inbound orders from Gmail to Arcadia"
```

Omni will call: `run_full_pipeline`

---

## 🔄 Update the Server

When you make changes:

```bash
# Stop the server
pkill -f "uvicorn mcp.server:app"

# Pull latest changes (if using git)
git pull

# Reinstall
pip install -e .[mcp]

# Restart server
uvicorn mcp.server:app --host 0.0.0.0 --port 8080 &
```

---

## ✅ Verification Checklist

Before connecting to Omni:

- [ ] Server starts without errors
- [ ] Health check returns `{"status": "ok"}`
- [ ] Tools endpoint lists 4 tools
- [ ] MCP initialize call succeeds
- [ ] ngrok URL is accessible from outside
- [ ] API key is set in environment
- [ ] Automation scripts exist in `../stagehand-test/`

---

## 🎯 Summary

**To connect to Omni:**

1. Install: `pip install .[mcp]`
2. Start: `uvicorn mcp.server:app --host 0.0.0.0 --port 8080`
3. Expose: `ngrok http 8080`
4. Configure Omni: Use ngrok URL + `/mcp` endpoint
5. Test: Try calling a tool from Omni

**Your MCP endpoint will be:**
```
https://your-ngrok-id.ngrok.io/mcp
```

---

## 📚 Related Documentation

- **MCP Protocol:** See `mcp/server.py` for implementation
- **Tool Schemas:** See `mcp/schemas.py` for tool definitions
- **Architecture:** See `ARCHITECTURE.md` for design details
- **SDK Usage:** See `SDK_USAGE.md` if you want direct Python access

---

**The MCP server is a thin adapter - all business logic is in `core/`** ✅

This means Omni gets the same reliable automation as direct SDK usage!

