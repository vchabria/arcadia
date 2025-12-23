# 🐍 How to Use the Python SDK

## Quick Start (30 seconds)

### 1. Install the SDK

```bash
cd inbound_mcp
pip install .
```

That's it! No server, no HTTP, just pure Python.

---

### 2. Basic Usage

```python
from inbound_mcp.sdk import InboundOrderClient

# Initialize the client
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
```

---

## 📋 Complete Examples

### Example 1: Create a Single Order

```python
from inbound_mcp.sdk import InboundOrderClient

# Set your API key (or set NOVA_ACT_API_KEY environment variable)
import os
os.environ['NOVA_ACT_API_KEY'] = 'your-api-key'

# Initialize client
client = InboundOrderClient()

# Create order with all details
result = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER",
    delivery_date="12/25/2025",
    delivery_company="FedEx",
    comments="Rush order - urgent delivery"
)

# Check result
if result.status == "success":
    print(f"✅ Order created successfully!")
    print(f"   Confirmation ID: {result.confirmation_id}")
    print(f"   Master Bill: {result.master_bill_number}")
    print(f"   Product: {result.product_code}")
    print(f"   Quantity: {result.quantity} pallets")
else:
    print(f"❌ Order failed: {result.error}")
```

---

### Example 2: Extract Orders from Gmail

```python
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()

# Extract orders from Gmail
result = client.extract_gmail_orders()

print(f"Email: {result.email_subject}")
print(f"Status: {result.status}")
print(f"Orders found: {result.orders_count}")

# Process each order
for order in result.orders:
    print(f"\nMaster Bill: {order.master_bill_number}")
    print(f"Date: {order.date}")
    print(f"Split Load: {order.split_load}")
    
    for product in order.products:
        print(f"  - {product.product_code}: {product.quantity} pallets @ {product.temperature}")
```

---

### Example 3: Run Full Pipeline (Extract + Submit)

```python
from inbound_mcp.sdk import InboundOrderClient

client = InboundOrderClient()

# Run complete automation
result = client.run_pipeline()

print(f"Pipeline Status: {result.status}")
print(f"Email: {result.email_subject}")
print(f"Extracted: {result.orders_extracted} orders")
print(f"Submitted: {result.orders_submitted} orders")
print(f"Failed: {result.orders_failed} orders")

# Show successful orders
if result.successful_orders:
    print("\n✅ Successful Orders:")
    for order in result.successful_orders:
        print(f"   {order.master_bill_number}: {order.confirmation_id}")

# Show failed orders
if result.failed_orders:
    print("\n❌ Failed Orders:")
    for order in result.failed_orders:
        print(f"   {order.master_bill_number}: {order.error}")
```

---

### Example 4: Error Handling

```python
from inbound_mcp.sdk import InboundOrderClient
from core.errors import (
    ValidationError,
    ExtractionError,
    TimeoutError,
    InboundOrderError
)

client = InboundOrderClient()

try:
    # Attempt to create order
    result = client.create_order(
        master_bill_number="123456789",
        product_code="PP48F",
        quantity=24,
        temperature="FREEZER"
    )
    
    print(f"Result: {result.status}")
    
except ValidationError as e:
    print(f"❌ Invalid input: {e}")
    # Handle validation error (e.g., wrong format)
    
except TimeoutError as e:
    print(f"❌ Timed out after {e.timeout_seconds} seconds")
    # Handle timeout (retry, notify, etc.)
    
except ExtractionError as e:
    print(f"❌ Extraction failed: {e}")
    # Handle extraction error
    
except InboundOrderError as e:
    print(f"❌ General error: {e}")
    # Handle any other automation error
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    # Handle unexpected errors
```

---

### Example 5: Using Convenience Functions

```python
# Import convenience functions (no client instantiation needed)
from inbound_mcp.sdk import extract_orders, create_order, run_pipeline

# Quick extraction
result = extract_orders()
print(f"Found {result.orders_count} orders")

# Quick order creation
order = create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)
print(f"Order status: {order.status}")

# Quick pipeline run
pipeline = run_pipeline()
print(f"Submitted {pipeline.orders_submitted} orders")
```

---

### Example 6: Working with Data Models

```python
from core.schemas import (
    CreateOrderInput,
    ProductData,
    OrderData,
    EmailExtractionData
)

# Create product data
product1 = ProductData(
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)

product2 = ProductData(
    product_code="BTL18-1R",
    quantity=18,
    temperature="COOLER"
)

# Create order data
order = OrderData(
    date="12/22 Monday",
    master_bill_number="123456789",
    products=[product1, product2],
    split_load=True
)

# Create email extraction data
email_data = EmailExtractionData(
    email_subject="Inbound ATL - 12/22",
    orders=[order]
)

# Submit to Arcadia
from inbound_mcp.sdk import InboundOrderClient
client = InboundOrderClient()
result = client.submit_orders(email_data)

print(f"Submitted: {result.orders_submitted}")
print(f"Failed: {result.orders_failed}")
```

---

## 🎯 Use Cases

### Use Case 1: Script Automation

```python
#!/usr/bin/env python3
"""Daily order processing script"""

from inbound_mcp.sdk import InboundOrderClient
import logging

logging.basicConfig(level=logging.INFO)

def main():
    client = InboundOrderClient()
    
    # Run full pipeline
    result = client.run_pipeline()
    
    if result.status == "success":
        logging.info(f"✅ Processed {result.orders_submitted} orders")
    else:
        logging.error(f"❌ Pipeline failed: {result.error}")
        # Send alert, retry, etc.

if __name__ == "__main__":
    main()
```

---

### Use Case 2: Jupyter Notebook

```python
# Cell 1: Setup
from inbound_mcp.sdk import InboundOrderClient
import pandas as pd

client = InboundOrderClient()

# Cell 2: Extract orders
extraction = client.extract_gmail_orders()
print(f"Found {extraction.orders_count} orders")

# Cell 3: Convert to DataFrame for analysis
orders_data = []
for order in extraction.orders:
    for product in order.products:
        orders_data.append({
            'master_bill': order.master_bill_number,
            'date': order.date,
            'product': product.product_code,
            'quantity': product.quantity,
            'temperature': product.temperature
        })

df = pd.DataFrame(orders_data)
df.head()

# Cell 4: Create order
result = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)
result.status
```

---

### Use Case 3: CI/CD Integration

```python
"""
CI/CD test script
Tests order automation in pipeline
"""

from inbound_mcp.sdk import InboundOrderClient
import sys

def test_order_creation():
    """Test order creation"""
    client = InboundOrderClient()
    
    result = client.create_order(
        master_bill_number="123456789",
        product_code="PP48F",
        quantity=24,
        temperature="FREEZER"
    )
    
    assert result.status in ["success", "failed"], "Invalid status"
    return result.status == "success"

def main():
    """Run tests"""
    try:
        if test_order_creation():
            print("✅ Tests passed")
            sys.exit(0)
        else:
            print("❌ Tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

### Use Case 4: Scheduled Task (cron)

```bash
#!/bin/bash
# schedule_orders.sh
# Add to crontab: 0 9 * * * /path/to/schedule_orders.sh

cd /path/to/inbound_mcp

# Set API key
export NOVA_ACT_API_KEY="your-key"

# Run automation
python3 << EOF
from inbound_mcp.sdk import InboundOrderClient
import datetime

client = InboundOrderClient()
result = client.run_pipeline()

timestamp = datetime.datetime.now().isoformat()
print(f"[{timestamp}] Status: {result.status}")
print(f"[{timestamp}] Submitted: {result.orders_submitted}")
print(f"[{timestamp}] Failed: {result.orders_failed}")
EOF
```

---

## 📊 Available Methods

### InboundOrderClient Methods

```python
client = InboundOrderClient(api_key=None)  # Optional API key

# 1. Extract orders from Gmail
result = client.extract_gmail_orders()
# Returns: ExtractionResult

# 2. Submit orders to Arcadia
result = client.submit_orders(email_data)
# Returns: SubmissionResult

# 3. Create single order
result = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER",
    supplying_facility_number=None,  # Optional
    delivery_date=None,              # Optional
    delivery_company=None,           # Optional
    comments=None                    # Optional
)
# Returns: OrderResult

# 4. Run full pipeline
result = client.run_pipeline()
# Returns: PipelineResult
```

---

## 🔧 Configuration

### Setting API Key

**Option 1: Environment Variable (Recommended)**
```bash
export NOVA_ACT_API_KEY="your-api-key"
```

**Option 2: In Code**
```python
import os
os.environ['NOVA_ACT_API_KEY'] = 'your-api-key'
```

**Option 3: Client Constructor**
```python
client = InboundOrderClient(api_key="your-api-key")
```

---

### Temperature Values

Temperatures are automatically normalized:

```python
# These all work:
client.create_order(..., temperature="F")          # → FREEZER
client.create_order(..., temperature="FREEZER")    # → FREEZER
client.create_order(..., temperature="C")          # → COOLER
client.create_order(..., temperature="COOLER")     # → COOLER
client.create_order(..., temperature="R")          # → COOLER
client.create_order(..., temperature="FR")         # → FREEZER CRATES
```

---

## 🐛 Troubleshooting

### Import Error

```bash
# Error: ModuleNotFoundError: No module named 'inbound_mcp'

# Solution: Install the package
cd inbound_mcp
pip install -e .
```

---

### API Key Not Set

```python
# Error: API key not found

# Solution: Set the environment variable
import os
os.environ['NOVA_ACT_API_KEY'] = 'your-api-key'
```

---

### Validation Error

```python
# Error: Master bill number must be exactly 9 digits

# Solution: Ensure master bill is 9 digits
client.create_order(
    master_bill_number="123456789",  # Must be exactly 9 digits
    ...
)
```

---

### Script Not Found

```bash
# Error: FileNotFoundError: Script not found: .../extraction_only.py

# Solution: Ensure automation scripts exist
ls ../stagehand-test/extraction_only.py
ls ../stagehand-test/run_arcadia_only.py
```

---

## 📚 Documentation

- **Complete API Reference:** `SDK_USAGE.md` (1,200 lines)
- **Architecture Details:** `ARCHITECTURE.md`
- **Quick Start:** `QUICK_START.md`
- **Working Examples:** `example_usage.py`, `demo_sdk.py`

---

## 🎯 Key Features

✅ **No server required** - Pure Python, works in scripts/notebooks  
✅ **Type-safe** - Full Pydantic validation  
✅ **Error handling** - Structured exceptions  
✅ **Agent-safe** - Deterministic, no TTY required  
✅ **Easy to use** - Simple class-based API  

---

## 🚀 Quick Reference

```python
# Import
from inbound_mcp.sdk import InboundOrderClient

# Initialize
client = InboundOrderClient()

# Extract
extract = client.extract_gmail_orders()

# Create
order = client.create_order(
    master_bill_number="123456789",
    product_code="PP48F",
    quantity=24,
    temperature="FREEZER"
)

# Pipeline
pipeline = client.run_pipeline()

# Check result
if order.status == "success":
    print(f"Confirmation: {order.confirmation_id}")
```

---

**That's it! The SDK is designed to be simple and intuitive** ✨

