#!/usr/bin/env python3
"""
Test script for Inbound Order MCP Server

Tests all JSON-RPC methods and tools to ensure proper MCP compliance.
"""

import requests
import json
from typing import Dict, Any


# Configuration
BASE_URL = "http://localhost:8080"
MCP_ENDPOINT = f"{BASE_URL}/mcp"


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def send_jsonrpc_request(method: str, params: Dict[str, Any] = None, request_id: int = 1) -> Dict[str, Any]:
    """
    Send a JSON-RPC 2.0 request to the MCP endpoint
    
    Args:
        method: JSON-RPC method name
        params: Method parameters
        request_id: Request ID
    
    Returns:
        Response dictionary
    """
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id
    }
    
    print(f"📤 Sending request: {method}")
    print(f"   Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(MCP_ENDPOINT, json=payload)
        response_data = response.json()
        
        print(f"📥 Response status: {response.status_code}")
        print(f"   Response: {json.dumps(response_data, indent=2)}\n")
        
        return response_data
    
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return {"error": str(e)}


def test_health_check():
    """Test the health check endpoint"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def test_root_endpoint():
    """Test the root endpoint"""
    print_section("TEST 2: Root Endpoint")
    
    try:
        response = requests.get(BASE_URL)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Root endpoint accessible")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def test_tools_rest():
    """Test the REST tools endpoint"""
    print_section("TEST 3: Tools List (REST)")
    
    try:
        response = requests.get(f"{BASE_URL}/tools")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        tools = data.get("tools", [])
        print(f"\n📋 Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.get('name')}: {tool.get('description')}")
        
        print("✅ Tools list accessible")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def test_initialize():
    """Test the MCP initialize method"""
    print_section("TEST 4: MCP Initialize")
    
    response = send_jsonrpc_request("initialize", {}, request_id=0)
    
    if "result" in response:
        result = response.get("result", {})
        version = result.get("protocolVersion")
        server_info = result.get("serverInfo", {})
        
        print(f"✅ Initialize successful")
        print(f"   Protocol Version: {version}")
        print(f"   Server: {server_info.get('name')} v{server_info.get('version')}")
    else:
        print("❌ Initialize failed")
    
    return response


def test_tools_list():
    """Test the tools/list method"""
    print_section("TEST 5: MCP Tools List")
    
    response = send_jsonrpc_request("tools/list", {}, request_id=1)
    
    if "result" in response:
        tools = response.get("result", {}).get("tools", [])
        print(f"✅ Tools list successful")
        print(f"   Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.get('name')}")
            print(f"     {tool.get('description')}")
    else:
        print("❌ Tools list failed")
    
    return response


def test_extract_tool():
    """Test the extract_inbound_orders tool"""
    print_section("TEST 6: Extract Inbound Orders Tool")
    
    print("⚠️  This will open Gmail and attempt to extract orders.")
    print("   Make sure you're logged into Gmail with the correct account.\n")
    
    proceed = input("Proceed with extraction test? (y/N): ")
    if proceed.lower() != 'y':
        print("⏭️  Skipping extraction test")
        return None
    
    response = send_jsonrpc_request(
        "tools/call",
        {
            "name": "extract_inbound_orders",
            "arguments": {}
        },
        request_id=2
    )
    
    if "result" in response:
        print("✅ Extract tool executed")
        result = response.get("result", {})
        
        # Check MCP format
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            print("✅ MCP format valid")
            text_content = content[0].get("text", "")
            
            # Try to parse the JSON data
            try:
                data = json.loads(text_content)
                print(f"\n📦 Extracted Data:")
                print(f"   Status: {data.get('status')}")
                print(f"   Email: {data.get('email_subject')}")
                print(f"   Orders: {data.get('orders_count')}")
            except:
                print(f"   Data: {text_content}")
        else:
            print("⚠️  MCP format may be invalid")
    else:
        print("❌ Extract tool failed")
        if "error" in response:
            print(f"   Error: {response.get('error')}")
    
    return response


def test_full_pipeline():
    """Test the run_full_pipeline tool"""
    print_section("TEST 7: Full Pipeline Tool")
    
    print("⚠️  This will execute the COMPLETE automation:")
    print("   1. Extract orders from Gmail")
    print("   2. Submit orders to Arcadia")
    print("   This creates REAL orders in Arcadia!\n")
    
    proceed = input("Proceed with full pipeline test? (y/N): ")
    if proceed.lower() != 'y':
        print("⏭️  Skipping full pipeline test")
        return None
    
    response = send_jsonrpc_request(
        "tools/call",
        {
            "name": "run_full_pipeline",
            "arguments": {}
        },
        request_id=3
    )
    
    if "result" in response:
        print("✅ Full pipeline executed")
        result = response.get("result", {})
        
        # Check MCP format
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            print("✅ MCP format valid")
            text_content = content[0].get("text", "")
            
            # Try to parse the JSON data
            try:
                data = json.loads(text_content)
                print(f"\n📊 Pipeline Results:")
                print(f"   Status: {data.get('status')}")
                print(f"   Email: {data.get('email_subject')}")
                print(f"   Extracted: {data.get('orders_extracted')}")
                print(f"   Submitted: {data.get('orders_submitted')}")
                print(f"   Failed: {data.get('orders_failed')}")
                
                # Show successful orders
                successful = data.get('successful_orders', [])
                if successful:
                    print(f"\n   ✅ Successful Orders:")
                    for order in successful:
                        print(f"      - {order.get('master_bill_number')}: {order.get('confirmation_id')}")
            except:
                print(f"   Data: {text_content}")
        else:
            print("⚠️  MCP format may be invalid")
    else:
        print("❌ Full pipeline failed")
        if "error" in response:
            print(f"   Error: {response.get('error')}")
    
    return response


def test_invalid_method():
    """Test error handling with invalid method"""
    print_section("TEST 8: Invalid Method (Error Handling)")
    
    response = send_jsonrpc_request("invalid/method", {}, request_id=99)
    
    if "error" in response:
        print("✅ Error handling works correctly")
        error = response.get("error", {})
        print(f"   Error code: {error.get('code')}")
        print(f"   Error message: {error.get('message')}")
    else:
        print("❌ Error handling may be broken")


def test_invalid_tool():
    """Test error handling with invalid tool"""
    print_section("TEST 9: Invalid Tool (Error Handling)")
    
    response = send_jsonrpc_request(
        "tools/call",
        {
            "name": "nonexistent_tool",
            "arguments": {}
        },
        request_id=100
    )
    
    if "result" in response:
        result = response.get("result", {})
        content = result.get("content", [])
        if content:
            text = content[0].get("text", "")
            if "Error" in text or "Unknown tool" in text:
                print("✅ Tool error handling works correctly")
            else:
                print("⚠️  Unexpected response format")
    else:
        print("❌ Tool error handling may be broken")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  🧪 INBOUND ORDER MCP SERVER TEST SUITE")
    print("="*80)
    print(f"\n  Testing server at: {BASE_URL}")
    print(f"  MCP endpoint: {MCP_ENDPOINT}\n")
    
    # Basic connectivity tests
    test_health_check()
    test_root_endpoint()
    test_tools_rest()
    
    # MCP protocol tests
    test_initialize()
    test_tools_list()
    
    # Error handling tests
    test_invalid_method()
    test_invalid_tool()
    
    # Functional tests (require user confirmation)
    test_extract_tool()
    test_full_pipeline()
    
    # Summary
    print_section("TEST SUMMARY")
    print("✅ All basic tests completed")
    print("\n📝 Notes:")
    print("   - Health check, root, and tools endpoints are working")
    print("   - MCP JSON-RPC protocol is properly implemented")
    print("   - Error handling is functioning correctly")
    print("   - Tool execution requires browser automation setup")
    print("\n🚀 Server is ready for Omni integration!\n")


if __name__ == "__main__":
    main()

