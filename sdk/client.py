"""
Python SDK Client for Inbound Order Automation

Provides a clean, class-based interface for agent-safe local Python usage.
No server dependencies, subprocess-safe, deterministic.
"""

from typing import Optional
import sys
from pathlib import Path

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    extract_orders_from_gmail,
    submit_orders_to_arcadia,
    create_single_arcadia_order,
    run_complete_pipeline,
)

from core.schemas import (
    EmailExtractionData,
    CreateOrderInput,
    ExtractionResult,
    SubmissionResult,
    OrderResult,
    PipelineResult,
)

from core.errors import (
    InboundOrderError,
    ExtractionError,
    SubmissionError,
    ValidationError,
    ScriptExecutionError,
    TimeoutError,
)


class InboundOrderClient:
    """
    Python SDK client for inbound order automation
    
    Provides a clean interface for:
    - Extracting orders from Gmail
    - Submitting orders to Arcadia
    - Creating single orders
    - Running the complete pipeline
    
    All methods are agent-safe, deterministic, and raise Python exceptions on errors.
    
    Example:
        ```python
        from inbound_mcp.sdk import InboundOrderClient
        
        client = InboundOrderClient()
        
        # Extract orders from Gmail
        result = client.extract_gmail_orders()
        print(f"Extracted {result.orders_count} orders")
        
        # Create a single order
        order_result = client.create_order(
            master_bill_number="123456789",
            product_code="PP48F",
            quantity=24,
            temperature="FREEZER"
        )
        print(f"Order status: {order_result.status}")
        
        # Run full pipeline
        pipeline_result = client.run_pipeline()
        print(f"Submitted {pipeline_result.orders_submitted} orders")
        ```
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the client
        
        Args:
            api_key: Optional NovaAct API key (defaults to NOVA_ACT_API_KEY env var)
        """
        if api_key:
            import os
            os.environ['NOVA_ACT_API_KEY'] = api_key
    
    def extract_gmail_orders(self) -> ExtractionResult:
        """
        Extract inbound orders from Gmail
        
        Returns:
            ExtractionResult with email subject and extracted orders
        
        Raises:
            ExtractionError: If extraction fails
            TimeoutError: If script times out
        
        Example:
            ```python
            result = client.extract_gmail_orders()
            print(f"Found {result.orders_count} orders")
            for order in result.orders:
                print(f"  - {order.master_bill_number}: {len(order.products)} products")
            ```
        """
        return extract_orders_from_gmail()
    
    def submit_orders(self, email_data: EmailExtractionData) -> SubmissionResult:
        """
        Submit extracted orders to Arcadia
        
        Args:
            email_data: EmailExtractionData with orders to submit
        
        Returns:
            SubmissionResult with submission status and results
        
        Raises:
            SubmissionError: If submission completely fails
            ValidationError: If input validation fails
        
        Example:
            ```python
            # First extract orders
            extraction = client.extract_gmail_orders()
            
            # Then submit them
            result = client.submit_orders(EmailExtractionData(
                email_subject=extraction.email_subject,
                orders=extraction.orders
            ))
            
            print(f"Submitted: {result.orders_submitted}")
            print(f"Failed: {result.orders_failed}")
            ```
        """
        return submit_orders_to_arcadia(email_data)
    
    def create_order(
        self,
        master_bill_number: str,
        product_code: str,
        quantity: int,
        temperature: str,
        supplying_facility_number: Optional[str] = None,
        delivery_date: Optional[str] = None,
        delivery_company: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> OrderResult:
        """
        Create a single inbound order in Arcadia
        
        Args:
            master_bill_number: 9-digit master bill of lading number (required)
            product_code: Product SKU code (e.g., PP48F, BTL18-1R) (required)
            quantity: Number of pallets (required, must be >= 1)
            temperature: Storage temperature (FREEZER, COOLER, or FREEZER CRATES) (required)
            supplying_facility_number: Supplying facility order number (defaults to master_bill_number)
            delivery_date: Requested delivery date (MM/DD/YYYY or M/D format)
            delivery_company: Carrier/delivery company code (e.g., CHR, FedEx)
            comments: Additional comments or notes
        
        Returns:
            OrderResult with submission status and confirmation ID
        
        Raises:
            ValidationError: If input validation fails
            ScriptExecutionError: If script execution fails
            TimeoutError: If script times out
        
        Example:
            ```python
            result = client.create_order(
                master_bill_number="123456789",
                product_code="PP48F",
                quantity=24,
                temperature="FREEZER",
                delivery_date="12/25/2025",
                delivery_company="FedEx",
                comments="Urgent delivery"
            )
            
            if result.status == "success":
                print(f"Order created: {result.confirmation_id}")
            else:
                print(f"Order failed: {result.error}")
            ```
        """
        order_input = CreateOrderInput(
            master_bill_number=master_bill_number,
            product_code=product_code,
            quantity=quantity,
            temperature=temperature,
            supplying_facility_number=supplying_facility_number,
            delivery_date=delivery_date,
            delivery_company=delivery_company,
            comments=comments,
        )
        
        return create_single_arcadia_order(order_input)
    
    def run_pipeline(self) -> PipelineResult:
        """
        Execute the complete automation pipeline (extract + submit)
        
        Returns:
            PipelineResult with extraction and submission results
        
        Raises:
            ExtractionError: If extraction fails
            SubmissionError: If submission fails
        
        Example:
            ```python
            result = client.run_pipeline()
            
            print(f"Pipeline status: {result.status}")
            print(f"Extracted: {result.orders_extracted}")
            print(f"Submitted: {result.orders_submitted}")
            print(f"Failed: {result.orders_failed}")
            
            for order in result.successful_orders:
                print(f"✅ {order.master_bill_number}: {order.confirmation_id}")
            
            for order in result.failed_orders:
                print(f"❌ {order.master_bill_number}: {order.error}")
            ```
        """
        return run_complete_pipeline()


# Convenience functions for direct usage
def extract_orders() -> ExtractionResult:
    """
    Convenience function to extract orders without instantiating client
    
    Returns:
        ExtractionResult with extracted orders
    
    Example:
        ```python
        from inbound_mcp.sdk import extract_orders
        
        result = extract_orders()
        print(f"Extracted {result.orders_count} orders")
        ```
    """
    return InboundOrderClient().extract_gmail_orders()


def create_order(
    master_bill_number: str,
    product_code: str,
    quantity: int,
    temperature: str,
    **kwargs
) -> OrderResult:
    """
    Convenience function to create a single order without instantiating client
    
    Args:
        master_bill_number: 9-digit master bill of lading number
        product_code: Product SKU code
        quantity: Number of pallets
        temperature: Storage temperature
        **kwargs: Additional optional parameters
    
    Returns:
        OrderResult with submission status
    
    Example:
        ```python
        from inbound_mcp.sdk import create_order
        
        result = create_order(
            master_bill_number="123456789",
            product_code="PP48F",
            quantity=24,
            temperature="FREEZER"
        )
        ```
    """
    return InboundOrderClient().create_order(
        master_bill_number=master_bill_number,
        product_code=product_code,
        quantity=quantity,
        temperature=temperature,
        **kwargs
    )


def run_pipeline() -> PipelineResult:
    """
    Convenience function to run full pipeline without instantiating client
    
    Returns:
        PipelineResult with pipeline results
    
    Example:
        ```python
        from inbound_mcp.sdk import run_pipeline
        
        result = run_pipeline()
        print(f"Submitted {result.orders_submitted} orders")
        ```
    """
    return InboundOrderClient().run_pipeline()

