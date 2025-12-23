"""
FastAPI MCP Server for Inbound Order Automation

Implements JSON-RPC 2.0 protocol with MCP-compliant responses for Omni integration.
Exposes tools for Gmail extraction and Arcadia submission.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
import traceback
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from .handlers import extract_from_gmail, add_orders_to_arcadia, run_full_pipeline, create_arcadia_order
from .mcp_schema import success_response, error_response, get_tool_schemas

# Initialize FastAPI app
app = FastAPI(
    title="Inbound Order MCP Server",
    description="Model Context Protocol server for Gmail-to-Arcadia inbound order automation",
    version="1.0.0"
)

# CORS middleware for ngrok and Omni compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Pydantic models for JSON-RPC
class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = {}
    id: Optional[int] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[int] = None


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "service": "inbound_mcp"}


# Simple REST endpoint to list tools
@app.get("/tools")
async def list_tools():
    """REST endpoint to list available tools"""
    return {
        "tools": get_tool_schemas()
    }


# Main MCP endpoint with JSON-RPC 2.0 support
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    Main MCP endpoint supporting JSON-RPC 2.0 protocol
    
    Supported methods:
    - initialize: Start MCP session
    - tools/list: Get available tools
    - tools/call: Execute a specific tool
    """
    print(f"[DEBUG] POST /mcp - Headers: {dict(request.headers)}")
    try:
        # Parse JSON-RPC request
        body = await request.json()
        print(f"[DEBUG] POST /mcp - Body: {body}")
        jsonrpc_request = JSONRPCRequest(**body)
        print(f"[DEBUG] POST /mcp - Method: {jsonrpc_request.method}")
        
        # Route to appropriate handler
        if jsonrpc_request.method == "initialize":
            result = handle_initialize(jsonrpc_request.params)
        elif jsonrpc_request.method == "tools/list":
            result = handle_tools_list(jsonrpc_request.params)
        elif jsonrpc_request.method == "tools/call":
            result = await handle_tools_call(jsonrpc_request.params)
        else:
            return JSONResponse(
                status_code=200,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {jsonrpc_request.method}"
                    },
                    "id": jsonrpc_request.id
                }
            )
        
        # Return successful JSON-RPC response
        response_content = {
                "jsonrpc": "2.0",
                "result": result,
                "id": jsonrpc_request.id
            }
        print(f"[DEBUG] POST /mcp - Response (truncated): {str(response_content)[:200]}")
        return JSONResponse(
            status_code=200,
            content=response_content
        )
        
    except Exception as e:
        # Return JSON-RPC error response
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"❌ MCP Error: {error_msg}")
        print(error_trace)
        
        return JSONResponse(
            status_code=200,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": error_msg,
                    "data": {"traceback": error_trace}
                },
                "id": body.get("id") if isinstance(body, dict) else None
            }
        )


def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle MCP initialize method
    
    Returns server info and protocol version
    """
    # Accept the client's protocol version if provided
    client_protocol_version = params.get('protocolVersion', '2025-03-26') if params else '2025-03-26'
    
    return {
        "protocolVersion": client_protocol_version,
        "serverInfo": {
            "name": "Inbound Order MCP",
            "version": "1.0.0"
        },
        "capabilities": {
            "tools": {}
        }
    }


def handle_tools_list(params: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Handle tools/list method
    
    Returns available tools with their schemas
    """
    return {
        "tools": get_tool_schemas()
    }


async def handle_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle tools/call method
    
    Executes the requested tool and returns MCP-wrapped response
    
    Args:
        params: Must contain 'name' field with tool name and optional 'arguments'
    
    Returns:
        MCP-compliant response with content array
    """
    tool_name = params.get("name")
    tool_args = params.get("arguments", {})
    
    if not tool_name:
        return error_response("Missing 'name' parameter in tools/call")
    
    try:
        # Route to appropriate tool handler
        if tool_name == "extract_inbound_orders":
            result = await extract_inbound_orders_tool(tool_args)
        elif tool_name == "add_to_arcadia":
            result = await add_to_arcadia_tool(tool_args)
        elif tool_name == "create_arcadia_order":
            result = await create_arcadia_order_tool(tool_args)
        elif tool_name == "run_full_pipeline":
            result = await run_full_pipeline_tool(tool_args)
        else:
            return error_response(f"Unknown tool: {tool_name}")
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"❌ Tool execution error: {error_msg}")
        print(error_trace)
        return error_response(f"{error_msg}\n\nTraceback:\n{error_trace}")


# Thread pool for running synchronous NovaAct code
executor = ThreadPoolExecutor(max_workers=3)

# Tool implementations
async def extract_inbound_orders_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Extract inbound orders from Gmail
    
    Returns MCP-wrapped extraction results
    """
    try:
        # Run synchronous NovaAct code in a thread to avoid event loop conflict
        loop = asyncio.get_event_loop()
        order_data = await loop.run_in_executor(executor, extract_from_gmail)
        
        if not order_data:
            return error_response("No valid 'Inbound ATL' email found from Arjun")
        
        return success_response({
            "status": "success",
            "email_subject": order_data.get('email_subject'),
            "orders_count": len(order_data.get('orders', [])),
            "orders": order_data.get('orders', [])
        })
        
    except Exception as e:
        return error_response(f"Gmail extraction failed: {str(e)}")


async def add_to_arcadia_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Add orders to Arcadia
    
    Expects 'order_data' in args with email_subject and orders array
    """
    try:
        order_data = args.get("order_data")
        
        if not order_data:
            return error_response("Missing 'order_data' parameter")
        
        # Run synchronous NovaAct code in a thread
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(executor, add_orders_to_arcadia, order_data)
        
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') == 'failed']
        
        return success_response({
            "status": "success" if not failed else "partial",
            "orders_submitted": len(successful),
            "orders_failed": len(failed),
            "successful_orders": successful,
            "failed_orders": failed
        })
        
    except Exception as e:
        return error_response(f"Arcadia submission failed: {str(e)}")


async def create_arcadia_order_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Create a single Arcadia order with all fields
    
    Accepts individual order parameters and creates order in Arcadia
    """
    try:
        # Run synchronous NovaAct code in a thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, create_arcadia_order, args)
        
        if result.get('status') == 'failed':
            return error_response(f"Order creation failed: {result.get('error')}")
        
        return success_response(result)
        
    except Exception as e:
        return error_response(f"Arcadia order creation failed: {str(e)}")


async def run_full_pipeline_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Run complete pipeline (extract + submit)
    
    Executes both Gmail extraction and Arcadia submission
    """
    try:
        # Run synchronous NovaAct code in a thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, run_full_pipeline)
        
        if result.get('status') == 'failed':
            return error_response(
                f"Pipeline failed at {result.get('stage')}: {result.get('error')}"
            )
        
        return success_response(result)
        
    except Exception as e:
        return error_response(f"Pipeline execution failed: {str(e)}")


# Root endpoint - GET for info
@app.get("/")
async def root(request: Request):
    """Root endpoint with service information"""
    accept_header = request.headers.get('accept', '')
    print(f"[DEBUG] GET / - Accept header: '{accept_header}'")
    print(f"[DEBUG] GET / - User-Agent: '{request.headers.get('user-agent', '')}'")
    
    # If client wants SSE, return error since GET doesn't support JSON-RPC
    if 'text/event-stream' in accept_header:
        from starlette.responses import JSONResponse
        return JSONResponse(
            status_code=405,
            content={
                "error": "Method Not Allowed",
                "message": "SSE/streaming not supported on GET. Use POST to /mcp endpoint for MCP protocol."
            }
        )
    
    return {
        "service": "Inbound Order MCP Server",
        "version": "1.0.0",
        "protocol": "JSON-RPC 2.0",
        "mcp_version": "2025-01",
        "endpoints": {
            "mcp": "/mcp (POST) - Main MCP JSON-RPC endpoint",
            "tools": "/tools (GET) - List available tools",
            "health": "/health (GET) - Health check"
        },
        "available_tools": [
            "extract_inbound_orders",
            "add_to_arcadia", 
            "create_arcadia_order",
            "run_full_pipeline"
        ],
        "documentation": "Send JSON-RPC 2.0 requests to /mcp endpoint"
    }


# Root endpoint - POST for MCP (Omni compatibility)
@app.post("/")
async def root_mcp(request: Request):
    """Root endpoint also accepts MCP JSON-RPC for Omni compatibility"""
    accept_header = request.headers.get("accept", "")
    print(f"[DEBUG] Root POST - Accept header: '{accept_header}'")
    print(f"[DEBUG] Root POST - All headers: {dict(request.headers)}")
    
    # Omni's SSE client doesn't send Accept header, so check Content-Type and body
    try:
        body = await request.body()
        body_text = body.decode('utf-8')
        print(f"[DEBUG] Request body preview: {body_text[:200]}")
        
        # If it's a JSON-RPC request, return SSE format for Omni compatibility
        if '"jsonrpc"' in body_text and '"method"' in body_text:
            print("[DEBUG] Detected JSON-RPC request - using SSE response")
            # Parse body and return SSE
            import json as json_lib
            body_json = json_lib.loads(body_text)
            return await sse_endpoint_with_body(body_json)
    except Exception as e:
        print(f"[DEBUG] Error parsing body: {e}")
    
    return await mcp_endpoint(request)


# SSE endpoint for Omni compatibility
async def sse_endpoint(request: Request):
    """SSE streaming endpoint for MCP protocol"""
    async def event_generator():
        # Read the JSON-RPC request from the body
        body = await request.json()
        
        # Process through normal MCP handler
        response_data = await handle_mcp_request(body)
        
        # Send as SSE event
        yield {
            "data": json.dumps(response_data)
        }
    
    return EventSourceResponse(event_generator())

async def sse_endpoint_with_body(body: dict):
    """SSE streaming endpoint with pre-parsed body"""
    async def event_generator():
        # Process through normal MCP handler
        response_data = await handle_mcp_request(body)
        
        # Send as SSE event
        yield {
            "data": json.dumps(response_data)
        }
    
    return EventSourceResponse(event_generator())


async def handle_mcp_request(body: dict) -> dict:
    """Handle MCP JSON-RPC request and return response dict"""
    try:
        jsonrpc_request = JSONRPCRequest(**body)
        
        # Route to appropriate handler
        if jsonrpc_request.method == "initialize":
            result = handle_initialize(jsonrpc_request.params)
        elif jsonrpc_request.method == "tools/list":
            result = handle_tools_list(jsonrpc_request.params)
        elif jsonrpc_request.method == "tools/call":
            result = await handle_tools_call(jsonrpc_request.params)
        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {jsonrpc_request.method}"
                },
                "id": jsonrpc_request.id
            }
        
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": jsonrpc_request.id
        }
        
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            },
            "id": body.get("id") if isinstance(body, dict) else None
        }


# Root endpoint - POST for MCP (Omni compatibility)
@app.post("/mcp")
async def mcp_post_handler(request: Request):
    """MCP endpoint that supports both JSON and SSE"""
    # Check if client wants SSE
    accept_header = request.headers.get("accept", "")
    if "text/event-stream" in accept_header:
        return await sse_endpoint(request)
    return await mcp_endpoint(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

