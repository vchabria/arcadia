"""
Core business logic for inbound order automation

This package contains pure Python logic with no MCP or HTTP dependencies.
It is designed to be used as a local SDK or wrapped by an MCP server.
"""

from .actions import (
    extract_orders_from_gmail,
    submit_orders_to_arcadia,
    create_single_arcadia_order,
    run_complete_pipeline,
)

from .schemas import (
    ProductData,
    OrderData,
    EmailExtractionData,
    CreateOrderInput,
    OrderResult,
    ExtractionResult,
    SubmissionResult,
    PipelineResult,
)

from .errors import (
    InboundOrderError,
    ExtractionError,
    SubmissionError,
    ValidationError,
    ScriptExecutionError,
    TimeoutError,
)

__all__ = [
    # Actions
    "extract_orders_from_gmail",
    "submit_orders_to_arcadia",
    "create_single_arcadia_order",
    "run_complete_pipeline",
    # Schemas
    "ProductData",
    "OrderData",
    "EmailExtractionData",
    "CreateOrderInput",
    "OrderResult",
    "ExtractionResult",
    "SubmissionResult",
    "PipelineResult",
    # Errors
    "InboundOrderError",
    "ExtractionError",
    "SubmissionError",
    "ValidationError",
    "ScriptExecutionError",
    "TimeoutError",
]

