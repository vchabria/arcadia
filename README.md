# Arcadia Inbound Order MCP Server

Production-ready Model Context Protocol (MCP) server for automating Gmail-to-Arcadia inbound order processing.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

---

## 🎯 Overview

This MCP server provides automated tools for:
- **Extracting** inbound order data from Gmail emails
- **Creating** orders in Arcadia warehouse management system
- **Automating** the complete Gmail → Arcadia pipeline

Built with FastAPI, NovaAct browser automation, and MCP protocol support.

---

## 🚀 Quick Start

### Option 1: Deploy to Render (Recommended)

See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for complete deployment guide.

**Quick Deploy:**
1. Push this repo to GitHub
2. Create new Web Service on Render
3. Set environment variables:
   - `NOVA_ACT_API_KEY`
   - `MCP_SECRET`
4. Deploy!

### Option 2: Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd inbound_mcp

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NOVA_ACT_API_KEY="your_key_here"
export MCP_SECRET="your_secret_here"

# Install Playwright browsers
playwright install chromium

# Run server
uvicorn mcp.server:app --host 0.0.0.0 --port 8080
```

---

## 📋 Requirements

**Environment Variables:**
- `NOVA_ACT_API_KEY` - Browser automation API key (required)
- `MCP_SECRET` - API authentication secret (required for production)

**System Requirements:**
- Python 3.11+
- Chromium browser (auto-installed via Playwright)
- 1GB+ RAM recommended

---

## 🔧 MCP Tools Available

### 1. `create_arcadia_order`
Create a single inbound order in Arcadia with all details.

**Parameters:**
```json
{
  "master_bill_number": "123456789",
  "product_code": "PP48F",
  "quantity": 24,
  "temperature": "FREEZER",
  "delivery_date": "12/24/2025",
  "delivery_company": "CHR",
  "comments": "Additional notes"
}
```

### 2. `extract_inbound_orders`
Extract order data from Gmail "Inbound ATL" emails.

**Returns:** Parsed orders with master bills, products, quantities, and temperatures.

### 3. `add_to_arcadia`
Submit previously extracted orders to Arcadia system.

**Parameters:**
```json
{
  "order_data": {
    "email_subject": "Inbound ATL 12/24",
    "orders": [...]
  }
}
```

### 4. `run_full_pipeline`
Execute complete automation: Gmail extraction → Arcadia submission.

**No parameters required** - runs end-to-end automation.

---

## 🔐 Authentication

All API requests (except `/health`) require the `x-mcp-key` header:

```bash
curl -X POST https://your-server.com/mcp \
  -H "Content-Type: application/json" \
  -H "x-mcp-key: your_mcp_secret" \
  -d '{"jsonrpc": "2.0", ...}'
```

**Without authentication:**
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing x-mcp-key header"
}
```

---

## 📡 API Endpoints

### `GET /health`
Health check endpoint (no auth required)

```bash
curl https://your-server.com/health
# Response: {"status": "ok", "service": "inbound_mcp"}
```

### `GET /tools`
List available MCP tools

```bash
curl https://your-server.com/tools
# Returns: {"tools": [...]}
```

### `POST /mcp`
Main MCP endpoint (JSON-RPC 2.0)

**Supported methods:**
- `initialize` - Start MCP session
- `tools/list` - Get available tools
- `tools/call` - Execute a tool

---

## 🐳 Docker Deployment

**Build:**
```bash
docker build -t arcadia-mcp-server .
```

**Run:**
```bash
docker run -p 10000:10000 \
  -e NOVA_ACT_API_KEY="your_key" \
  -e MCP_SECRET="your_secret" \
  arcadia-mcp-server
```

---

## 📊 Architecture

```
┌─────────────┐
│   Gmail     │ ← Extract orders from email
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MCP Server │ ← FastAPI + MCP Protocol
│   (This)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  NovaAct    │ ← Browser automation
│  Automation │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Arcadia    │ ← Create inbound orders
└─────────────┘
```

**Components:**
- **FastAPI** - HTTP server and API framework
- **MCP Protocol** - Model Context Protocol for tool invocation
- **NovaAct** - Browser automation for Arcadia/Gmail
- **Core Logic** - Business logic separated from HTTP layer

---

## 🧪 Testing

**Health Check:**
```bash
curl http://localhost:8080/health
```

**Create Test Order:**
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "x-mcp-key: your_secret" \
  -d @test_create_order.json
```

---

## 📚 SDK Usage

The Python SDK is included for programmatic access:

```python
from sdk.client import InboundOrderClient

client = InboundOrderClient(
    base_url="https://your-server.com",
    api_key="your_mcp_secret"
)

# Create an order
result = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)
```

See [SDK_USAGE.md](./SDK_USAGE.md) for complete documentation.

---

## 🛠️ Development

**Project Structure:**
```
inbound_mcp/
├── mcp/
│   ├── server.py       # FastAPI app & MCP endpoints
│   └── schemas.py      # MCP response formatters
├── core/
│   ├── actions.py      # Business logic
│   ├── schemas.py      # Data models
│   └── errors.py       # Custom exceptions
├── sdk/
│   └── client.py       # Python SDK
├── Dockerfile          # Production container
├── requirements.txt    # Python dependencies
└── env.template        # Environment variable template
```

**Adding a New Tool:**
1. Add business logic to `core/actions.py`
2. Define schema in `core/schemas.py`
3. Add tool definition to `mcp/schemas.py`
4. Handle in `mcp/server.py` MCP endpoint

---

## 🔒 Security

- ✅ API key authentication via headers
- ✅ Environment-based secrets (no hardcoding)
- ✅ CORS configured for specific origins
- ✅ Health checks don't require auth
- ✅ All secrets in `.gitignore`

**Best Practices:**
- Rotate `MCP_SECRET` regularly
- Use HTTPS in production (Render provides this)
- Monitor logs for unauthorized access
- Keep `NOVA_ACT_API_KEY` secure

---

## 📖 Documentation

- [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) - Deploy to Render
- [SDK_USAGE.md](./SDK_USAGE.md) - Python SDK guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design details

---

## 🐛 Troubleshooting

**Service won't start:**
- Verify environment variables are set
- Check logs for missing dependencies
- Ensure port 10000 is available

**Authentication fails:**
- Verify `x-mcp-key` header matches `MCP_SECRET`
- Check header spelling (case-sensitive)

**Browser automation fails:**
- Verify `NOVA_ACT_API_KEY` is valid
- Check Nova Act account credits
- Ensure Chromium is installed

**Orders not creating:**
- Check browser profile has valid Arcadia login
- Verify order data format matches schema
- Review logs for detailed error messages

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📧 Support

For issues or questions:
- Check documentation files
- Review Render logs
- Test with curl commands
- Verify environment variables

---

**Status:** ✅ Production Ready

Deploy this MCP server to automate your Arcadia inbound order processing!
