# ✅ Omni MCP Server Setup - WORKING

## 🚀 Current Status
- ✅ MCP Server running on port 8080
- ✅ Ngrok tunnel: `https://4921e51710af.ngrok-free.app`
- ✅ Omni backend can discover tools (tested successfully!)
- ✅ All 4 tools available including `create_arcadia_order`

---

## 📋 Step-by-Step: Add Server to Omni

### Option 1: Via Omni Frontend (Recommended)

1. **Go to Omni Settings**
   - Click on your profile/settings
   - Navigate to **"MCP Servers"** or **"Integrations"**

2. **Add New MCP Server**
   - Click **"Add Server"** or **"+ New Connection"**

3. **Fill in these EXACT values:**
   ```
   Name: Arcadia Inbound Orders
   Type: HTTP (or "Standard HTTP")
   URL: https://4921e51710af.ngrok-free.app/mcp
   ```
   
   **Important Notes:**
   - Make sure you select **"HTTP"** transport (NOT SSE)
   - Include `/mcp` at the end of the URL
   - No authentication headers needed

4. **Save and Test**
   - Click Save/Connect
   - Omni should discover 4 tools
   - Look for `create_arcadia_order` in the tool list

---

### Option 2: Via API/Manual Configuration

If you have direct database access or config files:

```json
{
  "type": "http",
  "name": "Arcadia Inbound Orders",
  "qualified_name": "arcadia_inbound_mcp",
  "url": "https://4921e51710af.ngrok-free.app/mcp",
  "enabled": true,
  "config": {
    "url": "https://4921e51710af.ngrok-free.app/mcp"
  }
}
```

---

## 🧪 Test It Works

### Via curl (Backend Test):
```bash
curl -X POST https://coldchain-enterprise-operator.onrender.com/api/mcp/discover-custom-tools \
  -H "Content-Type: application/json" \
  -d '{
    "type": "http",
    "config": {
      "url": "https://4921e51710af.ngrok-free.app/mcp"
    }
  }'
```

**Expected Response:** `"success": true` with 4 tools listed

### Via Omni Chat:
Once connected, try asking:
```
"Create an Arcadia order for master bill 060920251, 
product PP48F, 24 pallets, freezer temp, 
delivery 6/9, carrier CHR, 
comments: Monday delivery - Frozen pallets"
```

---

## 📊 Available Tools

1. **`create_arcadia_order`** ⭐ (Main tool)
   - Creates single order with all fields
   - Includes: master_bill, product_code, quantity, temperature, delivery_date, carrier, comments

2. **`extract_inbound_orders`**
   - Extracts orders from Gmail

3. **`add_to_arcadia`**
   - Batch submit orders

4. **`run_full_pipeline`**
   - Complete Gmail → Arcadia automation

---

## 🔍 Troubleshooting

### "No tools found" in Omni UI
- ✅ Check: Did you select **"HTTP"** transport (not SSE)?
- ✅ Check: Is the URL `https://4921e51710af.ngrok-free.app/mcp` (with `/mcp`)?
- ✅ Check: Are both servers running? (see below)

### Verify Servers Are Running:
```bash
# Check processes
ps aux | grep -E "uvicorn|ngrok" | grep -v grep

# Check logs
tail -20 '/Users/varnikachabria/Downloads/omni x stagehand/inbound_mcp/server.log'

# Test local server
curl http://localhost:8080/

# Get current ngrok URL
curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'])"
```

### Restart Servers:
```bash
cd '/Users/varnikachabria/Downloads/omni x stagehand/inbound_mcp'

# Kill and restart MCP server
lsof -ti:8080 | xargs kill -9 2>/dev/null
sleep 2
source venv/bin/activate
export NOVA_ACT_API_KEY=557e17b4-cb5b-4325-991b-8d3c6c35e038
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload > server.log 2>&1 &

# Restart ngrok
pkill -f ngrok
sleep 2
ngrok http 8080 > /tmp/ngrok.log 2>&1 &
sleep 3

# Get new URL
curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data = json.load(sys.stdin); print('New URL:', data['tunnels'][0]['public_url'])"
```

---

## 🎯 Next Steps After Setup

1. Test creating a single order via Omni chat
2. If working, you can process batches from the Gmail file
3. Consider deploying to Render for permanent URL (no ngrok needed)

---

## ⚠️ Important Notes

- **Ngrok URL changes** every time you restart ngrok
  - Current URL: `https://4921e51710af.ngrok-free.app`
  - If you restart ngrok, update the URL in Omni settings
  
- **For production:** Deploy to Render/Railway for a permanent URL

- **Keep servers running:** See `DEPLOYMENT.md` for Docker/systemd setup

