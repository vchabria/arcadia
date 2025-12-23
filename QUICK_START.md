# Quick Start Guide

## 🚀 Get Started in 30 Seconds

### Option 1: Use Python SDK (Recommended)

```bash
# Install
cd inbound_mcp
pip install .

# Use
python3 << EOF
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()

# Create an order
result = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)

print(f"Status: {result.status}")
if result.status == "success":
    print(f"Confirmation: {result.confirmation_id}")
else:
    print(f"Error: {result.error}")
EOF
```

### Option 2: Run MCP Server

```bash
# Install with MCP support
cd inbound_mcp
pip install .[mcp]

# Start server
uvicorn mcp.server:app --host 0.0.0.0 --port 8080

# Test it
curl http://localhost:8080/health
```

---

## 📋 Common Tasks

### Extract Orders from Gmail

```python
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()
result = client.extract_gmail_orders()

print(f"Found {result.orders_count} orders")
for order in result.orders:
    print(f"  {order.master_bill_number}: {len(order.products)} products")
```

### Create a Single Order

```python
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()
order = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER",
    delivery_date="12/25/2025"
)

print(f"Status: {order.status}")
```

### Run Full Pipeline

```python
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()
result = client.run_pipeline()

print(f"Extracted: {result.orders_extracted}")
print(f"Submitted: {result.orders_submitted}")
print(f"Failed: {result.orders_failed}")
```

---

## 🔧 Configuration

### Set API Key

```bash
export NOVA_ACT_API_KEY="your-api-key"
```

Or in Python:

```python
import os
os.environ['NOVA_ACT_API_KEY'] = 'your-api-key'

from inbound_mcp.sdk import InboundOrderClient
client = InboundOrderClient()
```

---

## 🎯 One-Liners

### Convenience Functions

```python
from inbound_mcp.sdk import extract_orders, create_order, run_pipeline

# Extract
orders = extract_orders()

# Create
result = create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)

# Pipeline
pipeline = run_pipeline()
```

---

## 🐛 Troubleshooting

### Import Error

```bash
# Error: ModuleNotFoundError: No module named 'inbound_mcp'
pip install -e .
```

### API Key Not Set

```bash
# Error: NOVA_ACT_API_KEY not found
export NOVA_ACT_API_KEY="your-api-key"
```

### Script Not Found

```bash
# Error: Script not found: .../extraction_only.py
# Check that extraction scripts exist:
ls ../stagehand-test/extraction_only.py
ls ../stagehand-test/run_arcadia_only.py
```

---

## 📚 Learn More

- **Full SDK Guide:** [SDK_USAGE.md](SDK_USAGE.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Migration Guide:** [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Examples:** [example_usage.py](example_usage.py)

---

## ✅ Installation Options

```bash
# SDK only (minimal dependencies)
pip install .

# SDK + MCP server
pip install .[mcp]

# Everything (with browser automation)
pip install .[full]

# Development tools
pip install .[dev]
```

---

**That's it! You're ready to automate order processing** 🎉

