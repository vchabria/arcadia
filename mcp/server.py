"""
MCP Server - Thin adapter over core business logic

This module only handles:
- FastAPI/HTTP routing
- JSON-RPC 2.0 protocol
- MCP message formatting
- Error serialization

NO business logic should exist here.
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
import traceback
import asyncio
import json
import os
import glob
from concurrent.futures import ThreadPoolExecutor
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import core business logic
from core import (
    extract_orders_from_gmail,
    submit_orders_to_arcadia,
    create_single_arcadia_order,
    run_complete_pipeline,
)

from core.schemas import (
    EmailExtractionData,
    CreateOrderInput,
    OrderData,
)

from core.errors import InboundOrderError

from .schemas import (
    success_response,
    error_response,
    get_tool_schemas,
)


# Initialize FastAPI app
app = FastAPI(
    title="Inbound Order MCP Server",
    description="Model Context Protocol server for Gmail-to-Arcadia inbound order automation",
    version="1.0.0"
)

# CORS middleware for Omni compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# MCP Authentication Middleware
@app.middleware("http")
async def authenticate_mcp_requests(request: Request, call_next):
    """
    Validate MCP requests with Bearer token
    Skips auth for /health endpoint only
    
    Note: VNC runs on separate port 6080, not through FastAPI
    """
    # Skip authentication for health checks
    if request.url.path == "/health":
        return await call_next(request)
    
    # Get MCP secret from environment
    mcp_secret = os.getenv("MCP_SECRET")
    
    # If MCP_SECRET is not set, allow all requests (dev mode)
    if not mcp_secret:
        print("[WARNING] MCP_SECRET not set - authentication disabled!")
        return await call_next(request)
    
    # Validate Authorization Bearer token
    auth = request.headers.get("authorization")
    
    if not auth or not auth.lower().startswith("bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Unauthorized", "message": "Missing Bearer token"}
        )
    
    token = auth.split(" ", 1)[1].strip()
    
    if token != mcp_secret:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Unauthorized", "message": "Invalid Bearer token"}
        )
    
    return await call_next(request)


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


# Thread pool for running synchronous core code
executor = ThreadPoolExecutor(max_workers=3)


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
    Handle tools/call method - Route to appropriate tool
    
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
        # Route to appropriate tool handler (all are thin wrappers)
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
        
    except InboundOrderError as e:
        # Handle domain errors
        return error_response(f"{type(e).__name__}: {str(e)}")
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"❌ Tool execution error: {error_msg}")
        print(error_trace)
        return error_response(f"{error_msg}\n\nTraceback:\n{error_trace}")


# Tool implementations - Thin wrappers around core actions
async def extract_inbound_orders_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Extract inbound orders from Gmail
    
    Thin wrapper - delegates to core.extract_orders_from_gmail()
    """
    try:
        # Run synchronous core code in thread to avoid event loop conflict
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, extract_orders_from_gmail)
        
        if result.status != "success":
            return error_response(result.error or "Extraction failed")
        
        # Convert to MCP response format
        return success_response({
            "status": result.status,
            "email_subject": result.email_subject,
            "orders_count": result.orders_count,
            "orders": [order.model_dump() for order in result.orders]
        })
        
    except Exception as e:
        return error_response(f"Gmail extraction failed: {str(e)}")


async def add_to_arcadia_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Add orders to Arcadia
    
    Thin wrapper - delegates to core.submit_orders_to_arcadia()
    """
    try:
        order_data_dict = args.get("order_data")
        
        if not order_data_dict:
            return error_response("Missing 'order_data' parameter")
        
        # Parse into EmailExtractionData
        email_data = EmailExtractionData(
            email_subject=order_data_dict.get("email_subject", "Unknown"),
            orders=[OrderData(**order) for order in order_data_dict.get("orders", [])]
        )
        
        # Run synchronous core code in thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, submit_orders_to_arcadia, email_data)
        
        # Convert to MCP response format
        return success_response({
            "status": result.status,
            "orders_submitted": result.orders_submitted,
            "orders_failed": result.orders_failed,
            "successful_orders": [order.model_dump() for order in result.successful_orders],
            "failed_orders": [order.model_dump() for order in result.failed_orders]
        })
        
    except Exception as e:
        return error_response(f"Arcadia submission failed: {str(e)}")


async def create_arcadia_order_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Create a single Arcadia order
    
    Thin wrapper - delegates to core.create_single_arcadia_order()
    """
    try:
        # FIX: Ensure master_bill_number is a string before validation
        if "master_bill_number" in args:
            args["master_bill_number"] = str(args["master_bill_number"])
        
        # Parse and validate input using Pydantic schema
        order_input = CreateOrderInput(**args)
        
        # Run synchronous core code in thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, create_single_arcadia_order, order_input)
        
        if result.status == "failed":
            return error_response(f"Order creation failed: {result.error}")
        
        # Convert to MCP response format
        return success_response(result.model_dump())
        
    except Exception as e:
        return error_response(f"Arcadia order creation failed: {str(e)}")


async def run_full_pipeline_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Run complete pipeline (extract + submit)
    
    Thin wrapper - delegates to core.run_complete_pipeline()
    """
    try:
        # Run synchronous core code in thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, run_complete_pipeline)
        
        if result.status == "failed":
            return error_response(
                f"Pipeline failed at {result.stage}: {result.error}"
            )
        
        # Convert to MCP response format
        return success_response({
            "status": result.status,
            "email_subject": result.email_subject,
            "orders_extracted": result.orders_extracted,
            "orders_submitted": result.orders_submitted,
            "orders_failed": result.orders_failed,
            "successful_orders": [order.model_dump() for order in result.successful_orders],
            "failed_orders": [order.model_dump() for order in result.failed_orders]
        })
        
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


# Root endpoint - POST for MCP (Plain HTTP JSON-RPC)
@app.post("/")
async def root_mcp(request: Request):
    """Root endpoint accepts MCP JSON-RPC - returns plain JSON (no SSE)"""
    print(f"[DEBUG] Root POST - Headers: {dict(request.headers)}")
    
    # Forward directly to MCP endpoint (plain JSON response)
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


# Removed duplicate /mcp endpoint - using the main one at line 145


# ============================================================================
# SCREENSHOT ENDPOINTS
# ============================================================================

@app.get("/screenshots")
async def list_screenshots():
    """
    List all available screenshots (login success, login failed, and pre-submit forms).
    
    Returns a list of screenshot filenames sorted by timestamp (newest first).
    """
    try:
        # Look for screenshots in /tmp (Render) or current directory (local)
        screenshot_dir = "/tmp" if Path("/app").exists() else "."
        
        # Get all screenshot types
        login_success = glob.glob(f"{screenshot_dir}/login_success_*.png")
        login_failed = glob.glob(f"{screenshot_dir}/login_failed_*.png")
        forms_filled = glob.glob(f"{screenshot_dir}/form_filled_*.png")
        
        all_screenshots = login_success + login_failed + forms_filled
        all_screenshots.sort(reverse=True)  # Most recent first
        
        # Extract just the filenames
        screenshot_names = [Path(s).name for s in all_screenshots]
        
        return {
            "success": True,
            "screenshots": screenshot_names,
            "count": len(screenshot_names),
            "by_type": {
                "login_success": [Path(s).name for s in sorted(login_success, reverse=True)],
                "login_failed": [Path(s).name for s in sorted(login_failed, reverse=True)],
                "forms_filled": [Path(s).name for s in sorted(forms_filled, reverse=True)]
            },
            "directory": screenshot_dir,
            "note": "Screenshots show login attempts and completed order forms before submission"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list screenshots: {str(e)}"
        )


@app.get("/screenshots/{filename}")
async def get_screenshot(filename: str):
    """
    Download a specific screenshot by filename.
    
    Supported types:
    - login_success_YYYYMMDD_HHMMSS.png
    - login_failed_YYYYMMDD_HHMMSS.png
    - form_filled_YYYYMMDD_HHMMSS_MASTERBILL.png
    
    Args:
        filename: Name of the screenshot file
    
    Returns:
        The PNG image file
    """
    try:
        # Security: Only allow specific patterns to prevent directory traversal
        valid_prefixes = ["login_success_", "login_failed_", "form_filled_"]
        if not any(filename.startswith(prefix) for prefix in valid_prefixes) or not filename.endswith(".png"):
            raise HTTPException(
                status_code=400,
                detail="Invalid filename format. Expected: login_success_*.png, login_failed_*.png, or form_filled_*.png"
            )
        
        # Determine screenshot directory
        screenshot_dir = "/tmp" if Path("/app").exists() else "."
        file_path = Path(screenshot_dir) / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Screenshot not found: {filename}"
            )
        
        return FileResponse(
            path=str(file_path),
            media_type="image/png",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve screenshot: {str(e)}"
        )


@app.get("/screenshots/latest/download")
async def get_latest_screenshot():
    """
    Download the most recent screenshot (any type).
    
    Convenient endpoint to always get the latest screenshot without knowing the filename.
    """
    try:
        # Find all screenshots
        screenshot_dir = "/tmp" if Path("/app").exists() else "."
        patterns = [
            f"{screenshot_dir}/login_success_*.png",
            f"{screenshot_dir}/login_failed_*.png",
            f"{screenshot_dir}/form_filled_*.png"
        ]
        
        all_screenshots = []
        for pattern in patterns:
            all_screenshots.extend(glob.glob(pattern))
        
        if not all_screenshots:
            raise HTTPException(
                status_code=404,
                detail="No screenshots found. No activity has occurred yet."
            )
        
        # Get most recent
        all_screenshots.sort(reverse=True)
        latest_screenshot = Path(all_screenshots[0])
        
        return FileResponse(
            path=str(latest_screenshot),
            media_type="image/png",
            filename=latest_screenshot.name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve latest screenshot: {str(e)}"
        )


@app.get("/screenshots/latest/login")
async def get_latest_login_screenshot():
    """
    Download the most recent login screenshot (success or failed).
    """
    try:
        screenshot_dir = "/tmp" if Path("/app").exists() else "."
        login_screenshots = []
        login_screenshots.extend(glob.glob(f"{screenshot_dir}/login_success_*.png"))
        login_screenshots.extend(glob.glob(f"{screenshot_dir}/login_failed_*.png"))
        
        if not login_screenshots:
            raise HTTPException(
                status_code=404,
                detail="No login screenshots found."
            )
        
        login_screenshots.sort(reverse=True)
        latest = Path(login_screenshots[0])
        
        return FileResponse(
            path=str(latest),
            media_type="image/png",
            filename=latest.name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve latest login screenshot: {str(e)}"
        )


@app.get("/screenshots/latest/form")
async def get_latest_form_screenshot():
    """
    Download the most recent pre-submit form screenshot.
    """
    try:
        screenshot_dir = "/tmp" if Path("/app").exists() else "."
        form_screenshots = glob.glob(f"{screenshot_dir}/form_filled_*.png")
        
        if not form_screenshots:
            raise HTTPException(
                status_code=404,
                detail="No form screenshots found. No orders have been created yet."
            )
        
        form_screenshots.sort(reverse=True)
        latest = Path(form_screenshots[0])
        
        return FileResponse(
            path=str(latest),
            media_type="image/png",
            filename=latest.name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve latest form screenshot: {str(e)}"
        )


# ============================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

