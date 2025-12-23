# Migration Guide: Old MCP Server → New Architecture

## Overview

This guide explains how to migrate from the old MCP server structure to the new refactored architecture.

---

## What Changed?

### Old Structure (Before)

```
inbound_mcp/
└── app/
    ├── main.py         # FastAPI + MCP + business logic all mixed
    ├── handlers.py     # Business logic + subprocess calls
    └── mcp_schema.py   # MCP response formatting
```

**Problems:**
- ❌ Business logic mixed with MCP protocol
- ❌ Cannot use without running server
- ❌ Not agent-safe for direct Python usage
- ❌ Logic duplication risk

### New Structure (After)

```
inbound_mcp/
├── core/              # ✅ Pure Python business logic
│   ├── actions.py
│   ├── schemas.py
│   └── errors.py
│
├── sdk/               # ✅ Python SDK (no server)
│   └── client.py
│
└── mcp/               # ✅ Thin MCP adapter
    ├── server.py
    └── schemas.py
```

**Benefits:**
- ✅ Business logic separated from protocol
- ✅ Can use SDK without server
- ✅ Agent-safe for direct Python usage
- ✅ No logic duplication

---

## Migration Path

### For Python Users (Recommended)

**Before:**
```python
# Had to run MCP server and make HTTP requests
import requests

response = requests.post("http://localhost:8080/mcp", json={
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "create_arcadia_order",
        "arguments": {...}
    },
    "id": 1
})
```

**After:**
```python
# Use SDK directly - no server needed!
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()
result = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)
```

---

### For MCP/Omni Users

**Before:**
```
POST http://localhost:8080/mcp
```

**After:**
```
POST http://localhost:8080/mcp  # Same endpoint!
```

**No changes required!** The MCP protocol is unchanged.

---

## Code Migration Examples

### Example 1: Extract Orders

**Before (via MCP):**
```python
response = requests.post("http://localhost:8080/mcp", json={
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "extract_inbound_orders",
        "arguments": {}
    },
    "id": 1
})

result = response.json()["result"]["content"][0]["text"]
data = json.loads(result)
```

**After (via SDK):**
```python
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()
result = client.extract_gmail_orders()

# Structured Pydantic model, not JSON string!
print(result.orders_count)
print(result.email_subject)
for order in result.orders:
    print(order.master_bill_number)
```

---

### Example 2: Create Order

**Before (via MCP):**
```python
response = requests.post("http://localhost:8080/mcp", json={
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
})
```

**After (via SDK):**
```python
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()
result = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)

if result.status == "success":
    print(f"Order created: {result.confirmation_id}")
else:
    print(f"Order failed: {result.error}")
```

---

### Example 3: Full Pipeline

**Before (via MCP):**
```python
response = requests.post("http://localhost:8080/mcp", json={
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "run_full_pipeline",
        "arguments": {}
    },
    "id": 1
})

result_text = response.json()["result"]["content"][0]["text"]
data = json.loads(result_text)
print(f"Submitted {data['orders_submitted']} orders")
```

**After (via SDK):**
```python
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()
result = client.run_pipeline()

print(f"Submitted {result.orders_submitted} orders")
print(f"Failed {result.orders_failed} orders")

for order in result.successful_orders:
    print(f"✅ {order.confirmation_id}")
```

---

## Installation Changes

### Before

```bash
pip install -r requirements.txt
```

Installed everything (FastAPI, uvicorn, etc.) even if only using SDK.

### After

```bash
# SDK only (minimal dependencies)
pip install .

# SDK + MCP server
pip install .[mcp]

# Full install (everything)
pip install .[full]
```

Install only what you need!

---

## Import Changes

### Before

```python
# Had to import from app module
from app.handlers import extract_from_gmail, create_arcadia_order
```

### After

```python
# Import from SDK (clean interface)
from inbound_mcp.sdk import InboundOrderClient

# Or import core directly (advanced)
from core import extract_orders_from_gmail, create_single_arcadia_order

# Or use convenience functions
from inbound_mcp.sdk import extract_orders, create_order
```

---

## Error Handling Changes

### Before

```python
# Errors were strings in JSON
try:
    response = requests.post(...)
    result = response.json()
    if "error" in result:
        print(f"Error: {result['error']}")
except Exception as e:
    print(f"Request failed: {e}")
```

### After

```python
# Errors are structured exceptions
from core.errors import (
    ExtractionError,
    SubmissionError,
    ValidationError,
    TimeoutError
)

try:
    result = client.extract_gmail_orders()
except TimeoutError as e:
    print(f"Timed out after {e.timeout_seconds}s")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
except ValidationError as e:
    print(f"Invalid input: {e}")
```

---

## Server Configuration Changes

### Before

```bash
# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### After

```bash
# Start server (new location)
uvicorn mcp.server:app --host 0.0.0.0 --port 8080
```

**Note:** The old `app/main.py` is still there for backwards compatibility, but the new `mcp/server.py` is the recommended entry point.

---

## Testing Changes

### Before

```python
# Had to test via HTTP requests
import requests

def test_extraction():
    response = requests.post("http://localhost:8080/mcp", ...)
    assert response.status_code == 200
```

### After

```python
# Can test SDK directly (no server needed!)
from inbound_mcp.sdk import InboundOrderClient

def test_extraction():
    client = InboundOrderClient()
    result = client.extract_gmail_orders()
    assert result.status == "success"
    assert result.orders_count >= 0
```

---

## Breaking Changes

### ❌ Removed

- Direct imports from `app.handlers` (use SDK instead)
- Direct calls to handler functions (use SDK methods)

### ✅ Still Works

- MCP server endpoints (`/mcp`, `/tools`, `/health`)
- MCP tool names and arguments
- JSON-RPC 2.0 protocol
- Environment variables (NOVA_ACT_API_KEY)

---

## Backwards Compatibility

### MCP Protocol

**100% compatible** - No changes to:
- Endpoint URLs
- JSON-RPC format
- Tool names
- Tool arguments
- Response format

### Python API

**Not backwards compatible** - Old handler functions are deprecated:
- `app.handlers.extract_from_gmail()` → `sdk.client.extract_gmail_orders()`
- `app.handlers.create_arcadia_order()` → `sdk.client.create_order()`
- `app.handlers.run_full_pipeline()` → `sdk.client.run_pipeline()`

---

## Migration Checklist

### For SDK Users

- [ ] Install new package: `pip install .`
- [ ] Update imports: `from inbound_mcp.sdk import InboundOrderClient`
- [ ] Replace handler calls with SDK methods
- [ ] Update error handling to use structured exceptions
- [ ] Test thoroughly

### For MCP Server Users

- [ ] Update server start command: `uvicorn mcp.server:app`
- [ ] No code changes needed (protocol unchanged)
- [ ] Test endpoints still work

### For Developers

- [ ] Update imports throughout codebase
- [ ] Update tests to use SDK
- [ ] Update documentation references
- [ ] Review error handling
- [ ] Run linter: `ruff check .`
- [ ] Run tests: `pytest`

---

## Rollback Plan

If you need to rollback to the old structure:

```bash
# Revert to old imports
from app.handlers import extract_from_gmail, create_arcadia_order

# Use old server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

**Note:** Old `app/` directory is still present for backwards compatibility during migration period.

---

## Support

### Getting Help

1. Check [SDK_USAGE.md](SDK_USAGE.md) for SDK examples
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for design details
3. Review error messages (they're designed to be helpful)
4. Check example scripts in `example_usage.py`

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'core'`
- **Solution:** Run `pip install -e .`

**Issue:** `ImportError: cannot import name 'InboundOrderClient'`
- **Solution:** Check your import: `from inbound_mcp.sdk import InboundOrderClient`

**Issue:** Old imports still work but are deprecated
- **Solution:** Update to SDK imports as shown in this guide

---

## Timeline

- **Phase 1 (Current):** Both old and new structure coexist
- **Phase 2 (Next):** Deprecation warnings on old imports
- **Phase 3 (Future):** Remove old `app/` directory

---

**Migration is straightforward and the new SDK is much easier to use!** 🚀

