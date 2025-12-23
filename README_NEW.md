# 🚀 Inbound Order Automation

**Agent-safe Python SDK and MCP server for automating Gmail-to-Arcadia order processing.**

## 📋 Overview

This project provides two ways to automate inbound order processing:

1. **Python SDK** - Direct Python library (no server required)
2. **MCP Server** - Model Context Protocol server for AI agent integration

Both share the same core business logic, ensuring consistency and maintainability.

---

## ✨ Features

- ✅ **Pure Python SDK** - Use directly in scripts, notebooks, or CI/CD
- ✅ **Agent-safe** - Deterministic, subprocess-safe, structured errors
- ✅ **Type-safe** - Full Pydantic validation
- ✅ **Thin MCP adapter** - Optional server layer with no logic duplication
- ✅ **No TTY required** - Works in automated environments
- ✅ **Proper error handling** - Structured exceptions, not silent failures

---

## 🏗️ Architecture

```
inbound_mcp/
├── core/                    # ✅ Pure Python business logic
│   ├── actions.py          # All real logic lives here
│   ├── schemas.py          # Pydantic models for I/O
│   └── errors.py           # Structured exceptions
│
├── sdk/                     # ✅ Python SDK (no server dependencies)
│   └── client.py           # Clean Python interface
│
└── mcp/                     # ✅ Optional MCP server (thin adapter)
    ├── server.py           # FastAPI + JSON-RPC wrapper
    └── schemas.py          # MCP response formatting
```

**Key Design Principles:**
- 🚫 No MCP imports in `core/`
- 🚫 No HTTP/FastAPI in `core/` or `sdk/`
- 🚫 No duplicated logic between SDK and MCP
- ✅ Core is pure Python and deterministic
- ✅ MCP is a thin wrapper around core

---

## 📦 Installation

### Option 1: SDK Only (Recommended for most use cases)

```bash
pip install .
```

This installs only the core SDK with minimal dependencies.

### Option 2: SDK + MCP Server

```bash
pip install .[mcp]
```

This adds FastAPI and server dependencies.

### Option 3: Full Install (with browser automation)

```bash
pip install .[full]
```

This includes NovaAct and Playwright.

### Option 4: Development

```bash
pip install .[dev]
```

Adds testing and linting tools.

---

## 🎯 Quick Start

### Python SDK Usage

```python
from inbound_mcp.sdk import InboundOrderClient

# Initialize client
client = InboundOrderClient()

# Extract orders from Gmail
result = client.extract_gmail_orders()
print(f"Extracted {result.orders_count} orders")

# Create a single order
order = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)
print(f"Status: {order.status}")

# Run full pipeline (extract + submit)
pipeline = client.run_pipeline()
print(f"Submitted {pipeline.orders_submitted} orders")
```

### MCP Server Usage

```bash
# Start the server
uvicorn mcp.server:app --host 0.0.0.0 --port 8080

# Or use the convenience script
python -m mcp.server
```

Then send JSON-RPC 2.0 requests:

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
    "id": 1
  }'
```

---

## 📚 Documentation

- **[SDK Usage Guide](SDK_USAGE.md)** - Complete SDK documentation
- **[MCP Integration](MCP_INTEGRATION.md)** - MCP server setup and usage
- **[Architecture](ARCHITECTURE.md)** - Design principles and structure

---

## 🧩 Available Operations

### 1. Extract Orders from Gmail

Extract inbound order data from Gmail "Inbound ATL" emails.

**SDK:**
```python
result = client.extract_gmail_orders()
```

**MCP:**
```json
{
  "name": "extract_inbound_orders",
  "arguments": {}
}
```

### 2. Create Single Order in Arcadia

Create a single inbound order with all details.

**SDK:**
```python
order = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER",
    delivery_date="12/25/2025"
)
```

**MCP:**
```json
{
  "name": "create_arcadia_order",
  "arguments": {
    "master_bill_number": "123456789",
    "product_code": "PP48F",
    "quantity": 24,
    "temperature": "FREEZER"
  }
}
```

### 3. Submit Multiple Orders

Submit extracted orders to Arcadia.

**SDK:**
```python
from core import EmailExtractionData

result = client.submit_orders(email_data)
```

**MCP:**
```json
{
  "name": "add_to_arcadia",
  "arguments": {
    "order_data": {
      "email_subject": "Inbound ATL - 6/9",
      "orders": [...]
    }
  }
}
```

### 4. Run Full Pipeline

Execute complete workflow (extract + submit).

**SDK:**
```python
pipeline = client.run_pipeline()
```

**MCP:**
```json
{
  "name": "run_full_pipeline",
  "arguments": {}
}
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
export NOVA_ACT_API_KEY="your-api-key"

# Optional
export PYTHON_PATH="/path/to/python3"
```

### Temperature Classification

Product codes determine temperature storage:

| Last Character | Temperature     |
|----------------|-----------------|
| `F`            | FREEZER         |
| `C`            | COOLER          |
| `R`            | COOLER          |
| `FR`           | FREEZER CRATES  |

---

## 🛠️ Development

### Project Structure

```
inbound_mcp/
├── core/               # Pure Python business logic (no MCP/HTTP)
│   ├── __init__.py
│   ├── actions.py     # Core automation functions
│   ├── schemas.py     # Pydantic models
│   └── errors.py      # Structured exceptions
│
├── sdk/                # Python SDK interface (no server)
│   ├── __init__.py
│   └── client.py      # Client class
│
├── mcp/                # Optional MCP server (thin adapter)
│   ├── __init__.py
│   ├── server.py      # FastAPI + JSON-RPC
│   └── schemas.py     # MCP response formatting
│
├── pyproject.toml      # Package configuration
├── setup.py            # Setup script
└── README.md           # This file
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy core sdk
```

---

## 🚦 Error Handling

All operations use structured exceptions:

```python
from core.errors import (
    ExtractionError,     # Gmail extraction failed
    SubmissionError,     # Arcadia submission failed
    ValidationError,     # Input validation failed
    ScriptExecutionError,# Script execution failed
    TimeoutError,        # Operation timed out
)

try:
    result = client.run_pipeline()
except ExtractionError as e:
    print(f"Extraction failed: {e}")
except SubmissionError as e:
    print(f"Submission failed: {e}")
except TimeoutError as e:
    print(f"Timeout after {e.timeout_seconds}s")
```

---

## 🎨 Agent Integration

The SDK is designed for AI agent use:

### ✅ Agent-Safe Features

- **No interactive input** - All subprocess calls are non-interactive
- **Deterministic** - Same input → same output
- **Structured errors** - Raises Python exceptions (no silent failures)
- **Timeouts** - Reasonable default timeouts (5 min)
- **Type-safe** - Full Pydantic validation

### Example Agent Usage

```python
from inbound_mcp.sdk import InboundOrderClient

def agent_task():
    """AI agent task to process orders"""
    client = InboundOrderClient()
    
    try:
        # Run full pipeline
        result = client.run_pipeline()
        
        # Check results
        if result.status == "success":
            return f"✅ Processed {result.orders_submitted} orders"
        elif result.status == "partial":
            return f"⚠️ Partial success: {result.orders_submitted} succeeded, {result.orders_failed} failed"
        else:
            return f"❌ Failed: {result.error}"
            
    except Exception as e:
        return f"❌ Error: {e}"
```

---

## 🌐 MCP Server for Omni

The MCP server provides JSON-RPC 2.0 compatibility for Omni integration:

### Start Server

```bash
uvicorn mcp.server:app --host 0.0.0.0 --port 8080
```

### Expose via ngrok

```bash
ngrok http 8080
```

### Configure in Omni

Use the ngrok URL: `https://your-id.ngrok.io/mcp`

---

## 📊 Response Formats

All operations return structured Pydantic models:

### ExtractionResult

```python
{
    "status": "success",
    "email_subject": "Inbound ATL - 6/9",
    "orders_count": 2,
    "orders": [
        {
            "master_bill_number": "123456789",
            "products": [
                {
                    "product_code": "PP48F",
                    "quantity": 24,
                    "temperature": "FREEZER"
                }
            ]
        }
    ]
}
```

### OrderResult

```python
{
    "status": "success",
    "master_bill_number": "123456789",
    "product_code": "PP48F",
    "quantity": 24,
    "temperature": "FREEZER",
    "confirmation_id": "ORD-123456789",
    "message": "Order created successfully"
}
```

### PipelineResult

```python
{
    "status": "success",
    "email_subject": "Inbound ATL - 6/9",
    "orders_extracted": 2,
    "orders_submitted": 2,
    "orders_failed": 0,
    "successful_orders": [...],
    "failed_orders": []
}
```

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=core --cov=sdk --cov=mcp
```

---

## 🐛 Troubleshooting

### Script Not Found

```bash
# Error: FileNotFoundError: Script not found

# Solution: Ensure extraction scripts exist in ../stagehand-test/
ls ../stagehand-test/extraction_only.py
ls ../stagehand-test/run_arcadia_only.py
```

### API Key Not Set

```bash
# Error: NOVA_ACT_API_KEY not found

# Solution: Set environment variable
export NOVA_ACT_API_KEY="your-api-key"
```

### Timeout Errors

```python
# Error: TimeoutError: Script timed out after 300 seconds

# Solution: Scripts have 5-minute timeout by default
# Check script logs to identify bottlenecks
```

---

## 📄 License

MIT License - Use freely for automation and integration.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes (keeping business logic in `core/`)
4. Add tests
5. Submit a pull request

---

## 📞 Support

For issues or questions:
- Check the [SDK Usage Guide](SDK_USAGE.md)
- Review error messages (they're designed to be helpful)
- Verify environment variables are set
- Check script logs for detailed information

---

**Built with ❤️ for agent-safe automation** 🤖

**Architecture:** Pure Python core → Thin SDK → Optional MCP adapter

