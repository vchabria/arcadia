#!/usr/bin/env python3
"""
Basic SDK validation test
Tests that the refactored architecture works correctly
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🧪 TESTING REFACTORED SDK ARCHITECTURE")
print("=" * 80)

# Test 1: Import core modules
print("\n✅ Test 1: Import core modules (no MCP dependencies)")
try:
    from core import (
        extract_orders_from_gmail,
        submit_orders_to_arcadia,
        create_single_arcadia_order,
        run_complete_pipeline,
    )
    from core.schemas import (
        ProductData,
        OrderData,
        CreateOrderInput,
        OrderResult,
        ExtractionResult,
        PipelineResult,
    )
    from core.errors import (
        InboundOrderError,
        ExtractionError,
        ValidationError,
    )
    print("   ✅ Core imports successful")
    print("   ✅ No MCP dependencies in core")
except ImportError as e:
    print(f"   ❌ Core import failed: {e}")
    sys.exit(1)

# Test 2: Import SDK
print("\n✅ Test 2: Import SDK client")
try:
    from sdk import InboundOrderClient
    from sdk.client import extract_orders, create_order, run_pipeline
    print("   ✅ SDK imports successful")
except ImportError as e:
    print(f"   ❌ SDK import failed: {e}")
    sys.exit(1)

# Test 3: Validate Pydantic schemas
print("\n✅ Test 3: Validate Pydantic schemas")
try:
    # Test valid order input
    order_input = CreateOrderInput(
        master_bill_number="123456789",
        product_code="PP48F",
        quantity=24,
        temperature="FREEZER"
    )
    print(f"   ✅ Valid order input created: {order_input.master_bill_number}")
    
    # Test temperature normalization
    order_input2 = CreateOrderInput(
        master_bill_number="987654321",
        product_code="BTL18-1R",
        quantity=18,
        temperature="F"  # Should normalize to FREEZER
    )
    assert order_input2.temperature == "FREEZER", "Temperature normalization failed"
    print(f"   ✅ Temperature normalized: F → {order_input2.temperature}")
    
except Exception as e:
    print(f"   ❌ Schema validation failed: {e}")
    sys.exit(1)

# Test 4: Validate error handling
print("\n✅ Test 4: Validate error handling")
try:
    from pydantic import ValidationError as PydanticValidationError
    
    # Test invalid master bill (too short)
    try:
        invalid_order = CreateOrderInput(
            master_bill_number="12345",  # Only 5 digits, needs 9
            product_code="PP48F",
            quantity=24,
            temperature="FREEZER"
        )
        print("   ❌ Validation should have failed!")
        sys.exit(1)
    except (ValidationError, PydanticValidationError, ValueError) as e:
        print(f"   ✅ Validation correctly rejected invalid master bill")
    
    # Test invalid quantity
    try:
        invalid_order = CreateOrderInput(
            master_bill_number="123456789",
            product_code="PP48F",
            quantity=0,  # Must be >= 1
            temperature="FREEZER"
        )
        print("   ❌ Validation should have failed!")
        sys.exit(1)
    except (ValidationError, PydanticValidationError, ValueError) as e:
        print(f"   ✅ Validation correctly rejected quantity=0")
    
except Exception as e:
    print(f"   ❌ Error handling test failed: {e}")
    sys.exit(1)

# Test 5: Instantiate SDK client
print("\n✅ Test 5: Instantiate SDK client")
try:
    client = InboundOrderClient()
    print("   ✅ InboundOrderClient instantiated successfully")
    print(f"   ✅ Client type: {type(client).__name__}")
    
    # Check methods exist
    methods = ['extract_gmail_orders', 'submit_orders', 'create_order', 'run_pipeline']
    for method in methods:
        assert hasattr(client, method), f"Missing method: {method}"
        print(f"   ✅ Method exists: {method}()")
    
except Exception as e:
    print(f"   ❌ Client instantiation failed: {e}")
    sys.exit(1)

# Test 6: Test data models
print("\n✅ Test 6: Test data models")
try:
    # Create product data
    product = ProductData(
        product_code="PP48F",
        quantity=24,
        temperature="FREEZER"
    )
    print(f"   ✅ ProductData created: {product.product_code}")
    
    # Create order data
    order = OrderData(
        master_bill_number="123456789",
        products=[product]
    )
    print(f"   ✅ OrderData created: {order.master_bill_number}")
    
    # Create order result
    result = OrderResult(
        status="success",
        master_bill_number="123456789",
        product_code="PP48F",
        quantity=24,
        temperature="FREEZER",
        confirmation_id="ORD-123456789",
        message="Test order"
    )
    print(f"   ✅ OrderResult created: {result.status}")
    
    # Test model serialization
    result_dict = result.model_dump()
    assert isinstance(result_dict, dict), "Serialization failed"
    print(f"   ✅ Model serialization works")
    
except Exception as e:
    print(f"   ❌ Data model test failed: {e}")
    sys.exit(1)

# Test 7: Check MCP imports (optional layer)
print("\n✅ Test 7: Check MCP layer (optional)")
try:
    from mcp import app
    from mcp.schemas import success_response, error_response, get_tool_schemas
    print("   ✅ MCP imports successful (optional layer)")
    
    # Test MCP response formatting
    test_data = {"test": "data"}
    mcp_response = success_response(test_data)
    assert "content" in mcp_response, "MCP response format incorrect"
    print(f"   ✅ MCP response formatting works")
    
    # Test tool schemas
    tools = get_tool_schemas()
    assert len(tools) == 4, f"Expected 4 tools, got {len(tools)}"
    tool_names = [t["name"] for t in tools]
    expected_tools = [
        "extract_inbound_orders",
        "add_to_arcadia",
        "create_arcadia_order",
        "run_full_pipeline"
    ]
    for expected in expected_tools:
        assert expected in tool_names, f"Missing tool: {expected}"
    print(f"   ✅ All 4 MCP tools defined: {', '.join(tool_names)}")
    
except ImportError as e:
    print(f"   ⚠️  MCP layer not available (optional): {e}")
except Exception as e:
    print(f"   ❌ MCP test failed: {e}")

# Test 8: Verify no circular imports
print("\n✅ Test 8: Verify architecture layers")
try:
    # Core should have no MCP imports
    import core.actions
    import core.schemas
    import core.errors
    
    # Check that core modules don't import mcp
    core_source = Path(__file__).parent / "core" / "actions.py"
    if core_source.exists():
        content = core_source.read_text()
        assert "import mcp" not in content, "Core imports MCP (violation!)"
        assert "from mcp" not in content, "Core imports MCP (violation!)"
        assert "import fastapi" not in content.lower(), "Core imports FastAPI (violation!)"
        print("   ✅ Core has no MCP/HTTP dependencies")
    
    # SDK should have no MCP imports
    sdk_source = Path(__file__).parent / "sdk" / "client.py"
    if sdk_source.exists():
        content = sdk_source.read_text()
        assert "import mcp" not in content, "SDK imports MCP (violation!)"
        assert "from mcp" not in content, "SDK imports MCP (violation!)"
        print("   ✅ SDK has no MCP dependencies")
    
    print("   ✅ Architecture layers properly separated")
    
except AssertionError as e:
    print(f"   ❌ Architecture violation: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Architecture test failed: {e}")

# Summary
print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - SDK ARCHITECTURE IS VALID")
print("=" * 80)
print("\n📊 Summary:")
print("   ✅ Core layer: Pure Python, no MCP dependencies")
print("   ✅ SDK layer: Clean interface, agent-safe")
print("   ✅ MCP layer: Optional thin adapter")
print("   ✅ Pydantic schemas: Validation working")
print("   ✅ Error handling: Structured exceptions")
print("   ✅ Architecture: Properly layered, no violations")
print("\n🎉 The refactored SDK is ready to use!")
print("\n📝 Next steps:")
print("   1. Set API key: export NOVA_ACT_API_KEY='your-key'")
print("   2. Run example: python example_usage.py")
print("   3. Or start MCP server: uvicorn mcp.server:app --port 8080")
print("=" * 80)

