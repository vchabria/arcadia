# Python SDK Usage Guide

## Overview

The Inbound Order Automation SDK provides a clean Python interface for automating Gmail-to-Arcadia order processing. It can be used directly in Python scripts, Jupyter notebooks, CI/CD pipelines, or by AI agents.

**Key Features:**
- ✅ Pure Python - no server required
- ✅ Agent-safe and deterministic
- ✅ Typed with Pydantic schemas
- ✅ Subprocess-safe (no TTY required)
- ✅ Structured error handling

---

## Installation

### SDK Only (No MCP Server)

```bash
pip install .
```

This installs only the core SDK with minimal dependencies (`pydantic` only).

### With MCP Server Support

```bash
pip install .[mcp]
```

This adds FastAPI and related dependencies for running the MCP server.

### Full Installation (Including Browser Automation)

```bash
pip install .[full]
```

This includes NovaAct and Playwright for browser automation.

### Development Installation

```bash
pip install .[dev]
```

This adds testing and linting tools.

---

## Quick Start

### Basic Usage

```python
from inbound_mcp.sdk import InboundOrderClient

# Initialize the client
client = InboundOrderClient()

# Extract orders from Gmail
result = client.extract_gmail_orders()
print(f"Extracted {result.orders_count} orders")

# Create a single order in Arcadia
order = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)
print(f"Order status: {order.status}")

# Run full pipeline (extract + submit)
pipeline = client.run_pipeline()
print(f"Submitted {pipeline.orders_submitted} orders")
```

---

## API Reference

### `InboundOrderClient`

Main client class for SDK operations.

#### `__init__(api_key: Optional[str] = None)`

Initialize the client with an optional API key.

```python
# Use environment variable NOVA_ACT_API_KEY
client = InboundOrderClient()

# Or provide API key explicitly
client = InboundOrderClient(api_key="your-api-key")
```

---

#### `extract_gmail_orders() -> ExtractionResult`

Extract inbound orders from Gmail.

**Returns:**
- `ExtractionResult` with email subject and list of orders

**Raises:**
- `ExtractionError` - If extraction fails
- `TimeoutError` - If script times out (5 min timeout)

**Example:**

```python
result = client.extract_gmail_orders()

print(f"Email: {result.email_subject}")
print(f"Status: {result.status}")
print(f"Orders: {result.orders_count}")

for order in result.orders:
    print(f"  Master Bill: {order.master_bill_number}")
    print(f"  Products: {len(order.products)}")
    for product in order.products:
        print(f"    - {product.product_code}: {product.quantity} pallets @ {product.temperature}")
```

---

#### `submit_orders(email_data: EmailExtractionData) -> SubmissionResult`

Submit extracted orders to Arcadia.

**Args:**
- `email_data` - `EmailExtractionData` object with orders to submit

**Returns:**
- `SubmissionResult` with submission status

**Raises:**
- `SubmissionError` - If submission completely fails
- `ValidationError` - If input validation fails

**Example:**

```python
from inbound_mcp.sdk import InboundOrderClient
from core import EmailExtractionData

# First extract
extraction = client.extract_gmail_orders()

# Build email data
email_data = EmailExtractionData(
    email_subject=extraction.email_subject,
    orders=extraction.orders
)

# Submit
result = client.submit_orders(email_data)

print(f"Status: {result.status}")
print(f"Submitted: {result.orders_submitted}")
print(f"Failed: {result.orders_failed}")

# Check results
for order in result.successful_orders:
    print(f"✅ {order.master_bill_number}: {order.confirmation_id}")

for order in result.failed_orders:
    print(f"❌ {order.master_bill_number}: {order.error}")
```

---

#### `create_order(...) -> OrderResult`

Create a single inbound order in Arcadia.

**Args:**
- `master_bill_number` (str, required) - 9-digit master bill of lading
- `product_code` (str, required) - Product SKU (e.g., "PP48F")
- `quantity` (int, required) - Number of pallets (>= 1)
- `temperature` (str, required) - "FREEZER", "COOLER", or "FREEZER CRATES"
- `supplying_facility_number` (str, optional) - Defaults to master_bill_number
- `delivery_date` (str, optional) - MM/DD/YYYY or M/D format
- `delivery_company` (str, optional) - Carrier code (e.g., "FedEx")
- `comments` (str, optional) - Additional notes

**Returns:**
- `OrderResult` with status and confirmation ID

**Raises:**
- `ValidationError` - If input validation fails
- `ScriptExecutionError` - If script execution fails
- `TimeoutError` - If script times out

**Example:**

```python
result = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER",
    delivery_date="12/25/2025",
    delivery_company="FedEx",
    comments="Rush order - deliver to dock 3"
)

if result.status == "success":
    print(f"✅ Order created: {result.confirmation_id}")
else:
    print(f"❌ Order failed: {result.error}")
```

---

#### `run_pipeline() -> PipelineResult`

Execute complete pipeline (extract from Gmail + submit to Arcadia).

**Returns:**
- `PipelineResult` with full pipeline results

**Raises:**
- `ExtractionError` - If extraction fails
- `SubmissionError` - If submission fails

**Example:**

```python
result = client.run_pipeline()

print(f"Pipeline status: {result.status}")
print(f"Email: {result.email_subject}")
print(f"Extracted: {result.orders_extracted} orders")
print(f"Submitted: {result.orders_submitted} orders")
print(f"Failed: {result.orders_failed} orders")

# Detailed results
for order in result.successful_orders:
    print(f"✅ {order.master_bill_number}")
    print(f"   Product: {order.product_code}")
    print(f"   Quantity: {order.quantity}")
    print(f"   Confirmation: {order.confirmation_id}")

for order in result.failed_orders:
    print(f"❌ {order.master_bill_number}: {order.error}")
```

---

## Convenience Functions

For simple use cases, you can use module-level convenience functions:

```python
from inbound_mcp.sdk import extract_orders, create_order, run_pipeline

# Extract orders
result = extract_orders()

# Create single order
order = create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)

# Run pipeline
pipeline = run_pipeline()
```

---

## Error Handling

All SDK methods raise structured exceptions:

```python
from core.errors import (
    ExtractionError,
    SubmissionError,
    ValidationError,
    ScriptExecutionError,
    TimeoutError,
    InboundOrderError  # Base exception
)

try:
    result = client.extract_gmail_orders()
except TimeoutError as e:
    print(f"Script timed out after {e.timeout_seconds} seconds")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
except InboundOrderError as e:
    print(f"General error: {e}")
```

---

## Data Models

### `ExtractionResult`

```python
class ExtractionResult:
    status: Literal["success", "failed"]
    email_subject: Optional[str]
    orders_count: int
    orders: List[OrderData]
    error: Optional[str]
```

### `OrderResult`

```python
class OrderResult:
    status: Literal["success", "failed"]
    master_bill_number: str
    product_code: Optional[str]
    quantity: Optional[int]
    temperature: Optional[str]
    confirmation_id: Optional[str]  # On success
    error: Optional[str]  # On failure
    message: Optional[str]
```

### `SubmissionResult`

```python
class SubmissionResult:
    status: Literal["success", "partial", "failed"]
    orders_submitted: int
    orders_failed: int
    successful_orders: List[OrderResult]
    failed_orders: List[OrderResult]
    error: Optional[str]
```

### `PipelineResult`

```python
class PipelineResult:
    status: Literal["success", "partial", "failed"]
    email_subject: Optional[str]
    orders_extracted: int
    orders_submitted: int
    orders_failed: int
    successful_orders: List[OrderResult]
    failed_orders: List[OrderResult]
    error: Optional[str]
    stage: Optional[str]  # Where failure occurred
```

---

## Agent Integration

The SDK is designed to be agent-safe:

### ✅ Safe Features

- **No interactive input** - All subprocess calls use `capture_output=True`
- **Deterministic** - Same input always produces same output
- **Structured errors** - All errors raise Python exceptions (no silent failures)
- **Timeouts** - Scripts have reasonable timeouts (5 min default)
- **Type-safe** - Full Pydantic validation on inputs and outputs

### ❌ Avoiding Pitfalls

```python
# ❌ Don't use subprocess.run directly
result = subprocess.run(["python", "script.py"])

# ✅ Use the SDK instead
result = client.run_pipeline()

# ❌ Don't parse stdout/stderr manually
output = subprocess.check_output(["curl", "..."]).decode()

# ✅ Use SDK's structured results
result = client.extract_gmail_orders()
print(result.orders_count)
```

---

## Jupyter Notebook Usage

```python
# Cell 1: Setup
from inbound_mcp.sdk import InboundOrderClient
import os

os.environ['NOVA_ACT_API_KEY'] = 'your-api-key'
client = InboundOrderClient()

# Cell 2: Extract orders
extraction = client.extract_gmail_orders()
extraction.orders

# Cell 3: Create single order
order = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)
order.status

# Cell 4: Run full pipeline
pipeline = client.run_pipeline()
print(f"Submitted {pipeline.orders_submitted}/{pipeline.orders_extracted} orders")
```

---

## CI/CD Usage

```yaml
# .github/workflows/test-orders.yml
name: Test Order Automation

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install SDK
        run: pip install .
      
      - name: Test extraction
        env:
          NOVA_ACT_API_KEY: ${{ secrets.NOVA_ACT_API_KEY }}
        run: |
          python -c "
          from inbound_mcp.sdk import extract_orders
          result = extract_orders()
          print(f'Extracted {result.orders_count} orders')
          "
```

---

## Production Best Practices

### 1. Environment Variables

```bash
export NOVA_ACT_API_KEY="your-api-key"
```

### 2. Error Handling

```python
from core.errors import InboundOrderError
import logging

logging.basicConfig(level=logging.INFO)

try:
    result = client.run_pipeline()
    logging.info(f"Pipeline succeeded: {result.orders_submitted} orders")
except InboundOrderError as e:
    logging.error(f"Pipeline failed: {e}")
    # Handle failure (retry, alert, etc.)
```

### 3. Monitoring

```python
import time

start = time.time()
result = client.run_pipeline()
duration = time.time() - start

print(f"Pipeline completed in {duration:.2f}s")
print(f"Success rate: {result.orders_submitted}/{result.orders_extracted}")
```

---

## Troubleshooting

### Script Not Found

```python
# Error: FileNotFoundError: Script not found: .../extraction_only.py

# Solution: Ensure extraction scripts exist in ../stagehand-test/
# The SDK looks for:
#   - stagehand-test/extraction_only.py (preferred)
#   - stagehand-test/add_inventory_from_tonya_email.py (fallback)
```

### Timeout Errors

```python
# Error: TimeoutError: Script timed out after 300 seconds

# Solution: Increase timeout in core/actions.py
# Or optimize the extraction script
```

### Validation Errors

```python
# Error: ValidationError: Master bill number must be exactly 9 digits

# Solution: Ensure master bill is 9 digits
order = client.create_order(
    master_bill_number="123456789",  # Must be 9 digits
    ...
)
```

---

## Support

For issues or questions:
- Check error messages (they're designed to be helpful)
- Review extraction script logs
- Verify API keys are set correctly
- Ensure browser profiles are accessible

---

**Built for agent-safe, deterministic automation** 🤖

