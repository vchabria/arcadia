"""
MCP Response Schema Helpers

Provides standardized response formatting for Omni-compatible MCP responses.
All tool responses must wrap data in the content array format.
"""

import json
from typing import Any, Dict, List


def success_response(data: Any) -> Dict[str, List[Dict[str, str]]]:
    """
    Create an MCP-compliant success response
    
    Args:
        data: Any JSON-serializable data
    
    Returns:
        MCP-formatted response with content array
    """
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(data, indent=2)
            }
        ]
    }


def error_response(message: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Create an MCP-compliant error response
    
    Args:
        message: Error message string
    
    Returns:
        MCP-formatted error response
    """
    return {
        "content": [
            {
                "type": "text",
                "text": f"Error: {message}"
            }
        ]
    }


def get_tool_schemas() -> List[Dict[str, Any]]:
    """
    Return MCP tool schemas for all available tools
    
    Returns:
        List of tool definitions with names, descriptions, and input schemas
    """
    return [
        {
            "name": "extract_inbound_orders",
            "description": "Extract inbound order data from Gmail 'Inbound ATL' emails from Arjun. Parses master bill numbers, product codes, quantities, and determines temperature type.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "add_to_arcadia",
            "description": "Submit extracted inbound orders to Arcadia system. Creates inbound orders with master bill numbers, product codes, quantities, and temperature settings.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "order_data": {
                        "type": "object",
                        "description": "Order data extracted from Gmail",
                        "properties": {
                            "email_subject": {"type": "string"},
                            "orders": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "master_bill_number": {"type": "string"},
                                        "products": {"type": "array"}
                                    }
                                }
                            }
                        }
                    }
                },
                "required": ["order_data"]
            }
        },
        {
            "name": "create_arcadia_order",
            "description": "Create a single inbound order in Arcadia with all details including master bill number, product code, quantity, temperature, delivery date, carrier, and comments/notes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "master_bill_number": {
                        "type": "string",
                        "description": "9-digit master bill of lading number (required)",
                        "pattern": "^[0-9]{9}$"
                    },
                    "supplying_facility_number": {
                        "type": "string",
                        "description": "Supplying facility order number (defaults to master_bill_number if not provided)"
                    },
                    "product_code": {
                        "type": "string",
                        "description": "Product SKU code (e.g., PP48F, BTL18-1R) (required)"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of pallets (required)",
                        "minimum": 1
                    },
                    "temperature": {
                        "type": "string",
                        "description": "Storage temperature: FREEZER, COOLER, or FREEZER CRATES (required)",
                        "enum": ["FREEZER", "COOLER", "FREEZER CRATES", "F", "C", "R", "FR"]
                    },
                    "delivery_date": {
                        "type": "string",
                        "description": "Requested delivery date (MM/DD/YYYY or M/D format)"
                    },
                    "delivery_company": {
                        "type": "string",
                        "description": "Carrier/delivery company code (e.g., CHR, FedEx)"
                    },
                    "comments": {
                        "type": "string",
                        "description": "Any additional comments or notes about the order"
                    }
                },
                "required": ["master_bill_number", "product_code", "quantity", "temperature"]
            }
        },
        {
            "name": "run_full_pipeline",
            "description": "Execute the complete automation pipeline: extract orders from Gmail, then submit them to Arcadia. Returns confirmation IDs for all processed orders.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]

