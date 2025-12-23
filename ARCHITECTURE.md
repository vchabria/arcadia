# Architecture Documentation

## Overview

This project follows a **layered architecture** where business logic is completely separated from protocol/server concerns.

```
┌─────────────────────────────────────────────┐
│          MCP Server (Optional)              │
│  FastAPI + JSON-RPC 2.0 + SSE              │
│  Thin adapter - NO business logic          │
└─────────────────┬───────────────────────────┘
                  │
                  │ Calls
                  ↓
┌─────────────────────────────────────────────┐
│        Python SDK (Recommended)             │
│  Class-based interface for direct use      │
│  InboundOrderClient                        │
└─────────────────┬───────────────────────────┘
                  │
                  │ Calls
                  ↓
┌─────────────────────────────────────────────┐
│       Core Business Logic (Pure Python)     │
│  - actions.py (all automation logic)       │
│  - schemas.py (Pydantic models)            │
│  - errors.py (structured exceptions)       │
│  NO MCP, HTTP, or server dependencies      │
└─────────────────────────────────────────────┘
```

---

## Design Principles

### 1. Separation of Concerns

**Core Layer** (`core/`)
- ✅ Pure Python business logic
- ✅ Deterministic functions
- ✅ No imports from `mcp/` or `sdk/`
- ✅ Subprocess-safe
- ❌ No FastAPI, HTTP, or MCP dependencies
- ❌ No server lifecycle management

**SDK Layer** (`sdk/`)
- ✅ Clean Python interface
- ✅ Wraps core functions
- ✅ Provides convenience methods
- ❌ No server dependencies
- ❌ No MCP protocol handling

**MCP Layer** (`mcp/`)
- ✅ Thin adapter over core
- ✅ JSON-RPC 2.0 protocol handling
- ✅ MCP message formatting
- ❌ No business logic
- ❌ No duplicate code

---

### 2. Dependency Flow

```
mcp/server.py
    ↓ imports
sdk/client.py
    ↓ imports
core/actions.py
    ↓ imports
core/schemas.py
core/errors.py
```

**Rules:**
- Core can only import from core
- SDK can import from core (not mcp)
- MCP can import from core and sdk
- NO circular imports

---

### 3. Error Handling

All errors are **structured exceptions**:

```python
core/errors.py
    ↓
InboundOrderError (base)
    ├── ExtractionError
    ├── SubmissionError
    ├── ValidationError
    ├── ScriptExecutionError
    └── TimeoutError
```

**Benefits:**
- Explicit error types
- Clear error messages
- Easy to catch and handle
- No silent failures

---

## Module Breakdown

### `core/actions.py`

**Purpose:** All business logic

**Functions:**
- `extract_orders_from_gmail()` - Extract from Gmail via subprocess
- `submit_orders_to_arcadia()` - Submit multiple orders
- `create_single_arcadia_order()` - Create one order
- `run_complete_pipeline()` - Full workflow

**Rules:**
- Pure Python functions
- No MCP/HTTP dependencies
- Uses subprocess for automation scripts
- Raises structured exceptions
- Returns Pydantic models

---

### `core/schemas.py`

**Purpose:** Type-safe input/output models

**Models:**
- `ProductData` - Single product in an order
- `OrderData` - Single order with products
- `EmailExtractionData` - Extracted email data
- `CreateOrderInput` - Input for creating order
- `OrderResult` - Result of order submission
- `ExtractionResult` - Result of extraction
- `SubmissionResult` - Result of submission
- `PipelineResult` - Result of full pipeline

**Benefits:**
- Automatic validation
- Type hints for IDE support
- Clear API contracts
- Easy serialization

---

### `core/errors.py`

**Purpose:** Structured exceptions

**Exceptions:**
- `InboundOrderError` - Base exception
- `ExtractionError` - Gmail extraction failed
- `SubmissionError` - Arcadia submission failed
- `ValidationError` - Input validation failed
- `ScriptExecutionError` - Script execution failed
- `TimeoutError` - Operation timed out

**Benefits:**
- Explicit error handling
- Clear error messages
- Easy to debug
- Agent-friendly

---

### `sdk/client.py`

**Purpose:** Python SDK interface

**Class:** `InboundOrderClient`

**Methods:**
- `extract_gmail_orders()` → `ExtractionResult`
- `submit_orders(email_data)` → `SubmissionResult`
- `create_order(...)` → `OrderResult`
- `run_pipeline()` → `PipelineResult`

**Convenience Functions:**
- `extract_orders()` - Quick extraction
- `create_order(...)` - Quick order creation
- `run_pipeline()` - Quick pipeline run

**Benefits:**
- Clean API
- No server required
- Direct Python usage
- Agent-safe

---

### `mcp/server.py`

**Purpose:** MCP protocol adapter

**Routes:**
- `GET /` - Service info
- `GET /health` - Health check
- `GET /tools` - List tools (REST)
- `POST /mcp` - Main MCP endpoint (JSON-RPC)

**JSON-RPC Methods:**
- `initialize` - Start session
- `tools/list` - List available tools
- `tools/call` - Execute tool

**Tool Handlers:**
- `extract_inbound_orders_tool()` - Thin wrapper
- `add_to_arcadia_tool()` - Thin wrapper
- `create_arcadia_order_tool()` - Thin wrapper
- `run_full_pipeline_tool()` - Thin wrapper

**Rules:**
- Only protocol handling
- Delegates to core functions
- No business logic
- Uses ThreadPoolExecutor for sync code

---

### `mcp/schemas.py`

**Purpose:** MCP response formatting

**Functions:**
- `success_response(data)` - MCP success format
- `error_response(message)` - MCP error format
- `get_tool_schemas()` - Tool definitions

**Benefits:**
- Consistent MCP format
- Omni-compatible
- Clear API contracts

---

## Data Flow

### Example: Create Order

```
1. User/Agent calls SDK
   client.create_order(master_bill="123456789", ...)

2. SDK validates and calls core
   CreateOrderInput(**args)
   create_single_arcadia_order(order_input)

3. Core executes business logic
   - Validates input
   - Runs subprocess
   - Captures output
   - Returns OrderResult

4. SDK returns to user
   OrderResult(status="success", confirmation_id="...")
```

### Example: MCP Tool Call

```
1. Omni sends JSON-RPC request
   POST /mcp
   {"method": "tools/call", "params": {"name": "create_arcadia_order", ...}}

2. MCP server routes to handler
   create_arcadia_order_tool(args)

3. Handler delegates to core
   CreateOrderInput(**args)
   create_single_arcadia_order(order_input)

4. Core executes and returns
   OrderResult(...)

5. MCP formats response
   success_response(result.model_dump())

6. Returns JSON-RPC response
   {"jsonrpc": "2.0", "result": {"content": [...]}}
```

---

## Subprocess Safety

All automation scripts run in subprocesses:

```python
subprocess.run(
    [python_cmd, str(script_path)],
    input=stdin_input,          # Provides input
    capture_output=True,        # Captures stdout/stderr
    text=True,                  # Text mode
    env=env,                    # Custom environment
    timeout=300,                # 5 minute timeout
    cwd=script_path.parent      # Set working directory
)
```

**Benefits:**
- No TTY required
- No async/event loop conflicts
- Clean environment isolation
- Proper timeout handling
- Exit code checking

---

## Testing Strategy

### Unit Tests (Core)

```python
def test_create_order_validation():
    """Test input validation"""
    with pytest.raises(ValidationError):
        CreateOrderInput(
            master_bill_number="12345",  # Too short
            product_code="PP48F",
            quantity=24,
            temperature="FREEZER"
        )
```

### Integration Tests (SDK)

```python
def test_sdk_create_order():
    """Test SDK order creation"""
    client = InboundOrderClient()
    result = client.create_order(
        master_bill_number="123456789",
        product_code="PP48F",
        quantity=24,
        temperature="FREEZER"
    )
    assert result.status in ["success", "failed"]
```

### API Tests (MCP)

```python
async def test_mcp_tool_call():
    """Test MCP tool execution"""
    response = await client.post("/mcp", json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "create_arcadia_order",
            "arguments": {...}
        },
        "id": 1
    })
    assert response.status_code == 200
    assert "result" in response.json()
```

---

## Installation Options

### 1. SDK Only (Minimal)

```bash
pip install .
```

Dependencies: `pydantic` only

Use case: Python scripts, notebooks, CI/CD

### 2. SDK + MCP Server

```bash
pip install .[mcp]
```

Dependencies: `pydantic`, `fastapi`, `uvicorn`, `sse-starlette`

Use case: Omni integration, remote access

### 3. Full (Everything)

```bash
pip install .[full]
```

Dependencies: All of above + `nova-act`, `playwright`

Use case: Complete local development

---

## Deployment Scenarios

### Scenario 1: Direct Python Usage

```python
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()
result = client.run_pipeline()
```

**Best for:**
- Python scripts
- Jupyter notebooks
- CI/CD pipelines
- Local automation

---

### Scenario 2: MCP Server (Local)

```bash
uvicorn mcp.server:app --host 127.0.0.1 --port 8080
```

**Best for:**
- Local Omni testing
- Development
- Single machine

---

### Scenario 3: MCP Server (Production)

```bash
# With ngrok
uvicorn mcp.server:app --host 0.0.0.0 --port 8080 &
ngrok http 8080
```

**Best for:**
- Remote Omni access
- Shared team access
- Cloud deployment

---

### Scenario 4: Docker Container

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install .[mcp]
CMD ["uvicorn", "mcp.server:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Best for:**
- Production deployment
- Kubernetes/cloud
- Consistent environments

---

## Performance Considerations

### Subprocess Overhead

- Each operation spawns a subprocess
- ~1-2 seconds overhead per call
- Acceptable for automation (5+ min tasks)
- Trade-off for stability and isolation

### Async Handling

- MCP server uses ThreadPoolExecutor
- Avoids async/sync conflicts
- Max 3 concurrent workers
- Can be increased if needed

### Memory Usage

- Minimal overhead (~50MB base)
- Browser automation adds ~500MB
- Subprocess isolation prevents leaks

---

## Security Considerations

### Environment Variables

```bash
export NOVA_ACT_API_KEY="your-api-key"
```

- Never hardcode API keys
- Use environment variables
- Rotate keys regularly

### Input Validation

- All inputs validated by Pydantic
- Master bill must be 9 digits
- Quantity must be >= 1
- Temperature must be valid enum

### Subprocess Isolation

- Scripts run in isolated processes
- Custom environment variables
- Timeout protection
- Exit code validation

---

## Maintenance

### Adding New Features

1. **Add to core/actions.py** - Business logic
2. **Add to core/schemas.py** - Input/output models
3. **Add to sdk/client.py** - SDK method
4. **Add to mcp/server.py** - MCP tool handler (if needed)
5. **Add to mcp/schemas.py** - Tool schema (if MCP)

### Updating Dependencies

```bash
# Update base dependencies
pip install --upgrade pydantic

# Update MCP dependencies
pip install --upgrade fastapi uvicorn

# Update all
pip install --upgrade -r requirements.txt
```

---

## Troubleshooting

### Import Errors

```python
# Error: ModuleNotFoundError: No module named 'core'

# Solution: Install package
pip install -e .
```

### Circular Imports

```python
# Error: ImportError: cannot import name 'X' from partially initialized module

# Solution: Check dependency flow (core → sdk → mcp)
# Never import from parent module
```

### Subprocess Failures

```python
# Error: ScriptExecutionError: Script failed with exit code 1

# Solution: Check script logs
# Verify script paths exist
# Check API keys are set
```

---

## Future Enhancements

### Potential Improvements

1. **Caching** - Cache extraction results
2. **Retry Logic** - Auto-retry failed operations
3. **Batch Processing** - Process multiple emails
4. **Webhooks** - Push notifications on completion
5. **Metrics** - Track success rates, timing
6. **Logging** - Structured logging to file/database

### Backwards Compatibility

- Core API is stable
- SDK methods follow semantic versioning
- MCP tools maintain input schemas
- Breaking changes only in major versions

---

**Architecture designed for:**
- ✅ Agent safety
- ✅ Maintainability
- ✅ Testability
- ✅ Extensibility
- ✅ No logic duplication

