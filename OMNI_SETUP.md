# 🚀 Omni Integration Guide - Arcadia Order Tool

## ✅ What's New

Added `create_arcadia_order` tool to your existing MCP server! Now you can create Arcadia orders with **ALL fields** including:

- ✅ Master Bill Number
- ✅ Product Code  
- ✅ Quantity
- ✅ Temperature
- ✅ Delivery Date
- ✅ Delivery Company
- ✅ **Comments/Notes** ← NEW!

---

## 🔌 How to Use in Omni

### 1. Start the MCP Server

```bash
cd '/Users/varnikachabria/Downloads/omni x stagehand/inbound_mcp'
source venv/bin/activate
export NOVA_ACT_API_KEY=557e17b4-cb5b-4325-991b-8d3c6c35e038
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 2. In Omni, Use the Tool

**Simple Order:**
```
Create an Arcadia order:
- Master Bill: 060920251
- Product: PP48F
- Quantity: 24 pallets
- Temperature: FREEZER
```

**Full Order with All Fields:**
```
Create an Arcadia order:
- Master Bill: 060920252
- Product: BTL18-1R  
- Quantity: 18 pallets
- Temperature: COOLER
- Delivery Date: 6/9/2025
- Carrier: CHR
- Comments: Priority delivery, handle with care
```

---

## 📝 JSON-RPC Format (if calling directly)

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "create_arcadia_order",
    "arguments": {
      "master_bill_number": "060920251",
      "product_code": "PP48F",
      "quantity": 24,
      "temperature": "FREEZER",
      "delivery_date": "6/9/2025",
      "delivery_company": "CHR",
      "comments": "Rush delivery"
    }
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"status\": \"success\", \"master_bill_number\": \"060920251\", \"confirmation_id\": \"ORD-060920251\", ...}"
      }
    ]
  },
  "id": 1
}
```

---

## 🧪 Test It

```bash
# Test the new tool
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d @test_create_order.json
```

---

## 🎯 Available Tools

Your MCP server now has **4 tools**:

| Tool | Description |
|------|-------------|
| `extract_inbound_orders` | Extract from Gmail |
| `add_to_arcadia` | Submit batch orders |
| `create_arcadia_order` | ⭐ **NEW** - Create single order with all fields |
| `run_full_pipeline` | Full automation |

---

## 📊 Temperature Auto-Detection

Product codes automatically set temperature:
- `PP48F` → FREEZER (ends with F)
- `BTL18-1R` → COOLER (ends with R or C)  
- `PP24FR` → FREEZER CRATES (ends with FR)

---

## 🔥 Quick Examples for Omni

### Example 1: Basic Order
> "Create Arcadia order 060920251 for PP48F, 24 pallets, freezer"

### Example 2: With Comments
> "Create Arcadia order 060920252, BTL18-1R, 18 pallets, cooler, add comment: urgent delivery"

### Example 3: Full Details
> "Create Arcadia order 060920253, PP24F, 6 pallets, freezer, delivery date 6/9, carrier CHR, comment: fragile items"

### Example 4: Multiple Orders
> "Create 3 Arcadia orders:
> 1. 060920251, PP48F, 24, freezer
> 2. 060920252, BTL18-1R, 18, cooler  
> 3. 060920253, PP24F, 6, freezer"

Omni will automatically call the tool 3 times!

---

## ✅ Setup Complete!

Your Omni MCP server now has the Arcadia order creation tool fully integrated. Just:

1. Start the server: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
2. Connect from Omni
3. Ask it to create orders in natural language!

**That's it!** 🎉

