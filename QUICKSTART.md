# ⚡ Quick Start Guide

Get the Inbound Order MCP Server running in 5 minutes.

---

## 🎯 Prerequisites

- Python 3.12+ installed
- Gmail account logged in (for email extraction)
- Arcadia account credentials (for order submission)

---

## 🚀 Method 1: Simple Startup (Recommended)

### Step 1: Run the startup script

```bash
cd inbound_mcp
./run_server.sh
```

That's it! The script will:
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create required directories
- ✅ Start the server

### Step 2: Test the server

Open a new terminal and run:

```bash
# Test health check
curl http://localhost:8080/health

# Test tool list
curl http://localhost:8080/tools

# Test MCP initialize
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 0}'
```

---

## 🐳 Method 2: Docker (Production)

### Step 1: Build and run with Docker Compose

```bash
cd inbound_mcp
docker-compose up --build
```

### Step 2: Test

```bash
curl http://localhost:8080/health
```

---

## 🧪 Method 3: Manual Testing Suite

### Run comprehensive tests:

```bash
cd inbound_mcp
python test_mcp.py
```

This will test:
- ✅ All endpoints (health, tools, root)
- ✅ JSON-RPC protocol compliance
- ✅ MCP response formatting
- ✅ Error handling
- ✅ Tool execution (with confirmation prompts)

---

## 🌐 Method 4: Expose via ngrok (For Omni)

### Step 1: Start the server

```bash
./run_server.sh
```

### Step 2: In another terminal, expose with ngrok

```bash
ngrok http 8080
```

### Step 3: Use the ngrok URL in Omni

Copy the `https://` URL from ngrok output and use it as your MCP endpoint:

```
https://your-id.ngrok.io/mcp
```

---

## 📋 Testing Individual Tools

### Test 1: Extract Orders from Gmail

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "extract_inbound_orders",
      "arguments": {}
    },
    "id": 1
  }'
```

### Test 2: Run Full Pipeline

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "run_full_pipeline",
      "arguments": {}
    },
    "id": 2
  }'
```

---

## 🔧 Troubleshooting

### Port 8080 already in use?

```bash
# Find process using port 8080
lsof -ti:8080 | xargs kill -9

# Or use a different port
uvicorn app.main:app --host 0.0.0.0 --port 8081
```

### Dependencies not installing?

```bash
# Upgrade pip first
pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

### Browser automation not working?

Make sure you've logged into Gmail and Arcadia manually at least once. The browser profiles are stored in:
- `contexts/gmail_profile/`
- `contexts/arcadia_profile/`

---

## 📊 Expected Response Format

All MCP tools return responses in this format:

### Success Response
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"status\": \"success\", \"data\": ...}"
      }
    ]
  },
  "id": 1
}
```

### Error Response
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: Something went wrong"
      }
    ]
  },
  "id": 1
}
```

---

## ✅ Verification Checklist

Before using with Omni, verify:

- [ ] `curl http://localhost:8080/health` returns `{"status":"ok"}`
- [ ] `curl http://localhost:8080/tools` returns tool list
- [ ] MCP initialize works (see Test 1 above)
- [ ] Browser profiles exist in `contexts/` directory
- [ ] Gmail account is logged in
- [ ] Arcadia account is logged in

---

## 🎯 Next Steps

1. **Local Testing**: Use `test_mcp.py` to verify all functionality
2. **Integration**: Expose via ngrok and connect to Omni
3. **Production**: Deploy with Docker or to Render/Railway
4. **Monitoring**: Check logs for any automation issues

---

## 📞 Quick Reference

| What | Command |
|------|---------|
| Start server | `./run_server.sh` |
| Test health | `curl localhost:8080/health` |
| Run tests | `python test_mcp.py` |
| Docker | `docker-compose up` |
| Expose | `ngrok http 8080` |

---

**Ready to automate! 🚀**

