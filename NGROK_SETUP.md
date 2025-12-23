# 🌐 Ngrok Setup - MCP Server Public Access

## ✅ Server Status

**✅ MCP Server:** Running on `localhost:8080`  
**✅ Ngrok Tunnel:** Active  
**🌐 Public URL:** `https://dce803adbf0e.ngrok-free.app`

---

## 🔌 Connect Omni to Your MCP Server

### **MCP Endpoint for Omni:**

```
https://dce803adbf0e.ngrok-free.app/mcp
```

---

## 🎯 Available Tools

Your MCP server exposes 4 tools:

| Tool Name | Description |
|-----------|-------------|
| `extract_inbound_orders` | Extract orders from Gmail |
| `add_to_arcadia` | Submit batch orders to Arcadia |
| **`create_arcadia_order`** | ⭐ Create single order with all fields |
| `run_full_pipeline` | Full Gmail→Arcadia automation |

---

## 📝 Example: Create Arcadia Order in Omni

Just tell Omni in natural language:

```
Create an Arcadia inbound order:
- Master Bill: 060920251
- Product: PP48F
- Quantity: 24 pallets
- Temperature: FREEZER
- Delivery Date: 6/9/2025
- Carrier: CHR
- Comments: Rush delivery, handle with care
```

Omni will automatically call your MCP server at the ngrok URL! 🎉

---

## 🧪 Test the Connection

### **Health Check:**
```bash
curl https://dce803adbf0e.ngrok-free.app/health
```

**Expected Response:**
```json
{"status":"ok","service":"inbound_mcp"}
```

### **List Tools:**
```bash
curl https://dce803adbf0e.ngrok-free.app/tools
```

### **Test Create Order Tool:**
```bash
curl -X POST https://dce803adbf0e.ngrok-free.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_arcadia_order",
      "arguments": {
        "master_bill_number": "060920251",
        "product_code": "PP48F",
        "quantity": 24,
        "temperature": "FREEZER",
        "comments": "Test order from ngrok"
      }
    },
    "id": 1
  }'
```

---

## 🔄 Restart Services

If you need to restart:

### **Restart MCP Server:**
```bash
cd '/Users/varnikachabria/Downloads/omni x stagehand/inbound_mcp'
source venv/bin/activate
export NOVA_ACT_API_KEY=557e17b4-cb5b-4325-991b-8d3c6c35e038

# Kill old server
lsof -ti:8080 | xargs kill -9

# Start new server
nohup uvicorn app.main:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &
```

### **Restart Ngrok:**
```bash
# Kill old ngrok
pkill ngrok

# Start new ngrok
ngrok http 8080
```

### **Get New Ngrok URL:**
```bash
curl http://localhost:4040/api/tunnels | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'])"
```

---

## 📊 Monitor Logs

### **Server Logs:**
```bash
tail -f /Users/varnikachabria/Downloads/omni\ x\ stagehand/inbound_mcp/server.log
```

### **Ngrok Dashboard:**
Open in browser: `http://localhost:4040`

---

## 🔒 Security Notes

- ✅ Ngrok provides HTTPS automatically
- ✅ MCP server has CORS enabled for Omni
- ⚠️ Free ngrok URLs change on restart
- ⚠️ Keep your Nova Act API key secure

---

## 📱 Omni Integration Steps

1. **Open Omni Settings** → MCP Servers
2. **Add New Server:**
   - Name: `Arcadia Order Processor`
   - URL: `https://dce803adbf0e.ngrok-free.app/mcp`
   - Type: `JSON-RPC 2.0`
3. **Save & Test Connection**
4. **Start using the tools!**

---

## 🎉 You're All Set!

**Endpoints:**
- 🏠 Server Info: `https://dce803adbf0e.ngrok-free.app/`
- 🔧 Health Check: `https://dce803adbf0e.ngrok-free.app/health`
- 🛠️ Tools List: `https://dce803adbf0e.ngrok-free.app/tools`
- 🚀 MCP Endpoint: `https://dce803adbf0e.ngrok-free.app/mcp`

Your MCP server is now **publicly accessible** and ready for Omni! 🌍

