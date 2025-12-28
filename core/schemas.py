"""
Pydantic schemas for type-safe input/output

All schemas are designed for agent-safe execution with clear validation rules.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime
import re


# Temperature types
TemperatureType = Literal["FREEZER", "COOLER", "FREEZER CRATES", "F", "C", "R", "FR"]


class ProductData(BaseModel):
    """Single product within an order"""
    product_code: str = Field(..., description="Product SKU code (e.g., PP48F, BTL18-1R)")
    quantity: int = Field(..., ge=1, description="Number of pallets (must be >= 1)")
    temperature: str = Field(..., description="Storage temperature classification")

    @field_validator('product_code')
    @classmethod
    def validate_product_code(cls, v: str) -> str:
        """Ensure product code is not empty"""
        if not v or not v.strip():
            raise ValueError("Product code cannot be empty")
        return v.strip()


class OrderData(BaseModel):
    """Single order with master bill and products"""
    date: Optional[str] = Field(None, description="Delivery date (e.g., '6/9 Monday')")
    master_bill_number: str = Field(..., description="9-digit master bill of lading number")
    supplying_facility_number: Optional[str] = Field(None, description="Supplying facility order number")
    split_load: bool = Field(False, description="Whether this is a split load")
    products: List[ProductData] = Field(..., min_length=1, description="List of products in this order")

    @field_validator('master_bill_number')
    @classmethod
    def validate_master_bill(cls, v: str) -> str:
        """Validate master bill number format (9 digits)"""
        v = v.strip()
        if not re.match(r'^\d{9}$', v):
            raise ValueError(f"Master bill number must be exactly 9 digits, got: {v}")
        return v

    @field_validator('products')
    @classmethod
    def validate_products(cls, v: List[ProductData]) -> List[ProductData]:
        """Ensure at least one product exists"""
        if not v:
            raise ValueError("Order must contain at least one product")
        return v


class EmailExtractionData(BaseModel):
    """Data extracted from Gmail email"""
    email_subject: str = Field(..., description="Subject line of the email")
    orders: List[OrderData] = Field(default_factory=list, description="List of orders extracted from email")
    extracted_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of extraction")


class CreateOrderInput(BaseModel):
    """Input for creating a single Arcadia order"""
    master_bill_number: str = Field(..., description="9-digit master bill of lading number")
    product_code: str = Field(..., description="Product SKU code (required)")
    quantity: int = Field(..., ge=1, description="Number of pallets (required)")
    temperature: TemperatureType = Field(..., description="Storage temperature (required)")
    supplying_facility_number: Optional[str] = Field(None, description="Defaults to master_bill_number if not provided")
    delivery_date: Optional[str] = Field(None, description="Requested delivery date (MM/DD/YYYY or M/D format)")
    delivery_company: Optional[str] = Field(None, description="Carrier/delivery company code")
    comments: Optional[str] = Field(None, description="Additional comments or notes")

    @field_validator('master_bill_number')
    @classmethod
    def validate_master_bill(cls, v: str) -> str:
        """Validate master bill number format"""
        v = v.strip()
        if not re.match(r'^\d{9}$', v):
            raise ValueError(f"Master bill number must be exactly 9 digits, got: {v}")
        return v

    @field_validator('temperature')
    @classmethod
    def normalize_temperature(cls, v: str) -> str:
        """Normalize temperature abbreviations to full names"""
        temp_map = {
            "F": "FREEZER",
            "C": "COOLER",
            "R": "COOLER",
            "FR": "FREEZER CRATES"
        }
        v_upper = v.upper().strip()
        return temp_map.get(v_upper, v_upper)


class OrderResult(BaseModel):
    """Result of a single order submission"""
    status: Literal["success", "failed"] = Field(..., description="Order submission status")
    master_bill_number: str = Field(..., description="Master bill number for this order")
    product_code: Optional[str] = Field(None, description="Product code")
    quantity: Optional[int] = Field(None, description="Quantity of pallets")
    temperature: Optional[str] = Field(None, description="Temperature classification")
    confirmation_id: Optional[str] = Field(None, description="Arcadia confirmation ID (on success)")
    error: Optional[str] = Field(None, description="Error message (on failure)")
    message: Optional[str] = Field(None, description="Human-readable status message")
    video_path: Optional[str] = Field(None, description="Path to recorded video of browser session (if available)")


class ExtractionResult(BaseModel):
    """Result of Gmail extraction operation"""
    status: Literal["success", "failed"] = Field(..., description="Extraction status")
    email_subject: Optional[str] = Field(None, description="Subject of extracted email")
    orders_count: int = Field(0, description="Number of orders extracted")
    orders: List[OrderData] = Field(default_factory=list, description="Extracted orders")
    error: Optional[str] = Field(None, description="Error message if extraction failed")


class SubmissionResult(BaseModel):
    """Result of Arcadia submission operation"""
    status: Literal["success", "partial", "failed"] = Field(..., description="Overall submission status")
    orders_submitted: int = Field(0, description="Number of orders successfully submitted")
    orders_failed: int = Field(0, description="Number of orders that failed")
    successful_orders: List[OrderResult] = Field(default_factory=list, description="Successfully submitted orders")
    failed_orders: List[OrderResult] = Field(default_factory=list, description="Failed order submissions")
    error: Optional[str] = Field(None, description="Error message if completely failed")


class PipelineResult(BaseModel):
    """Result of full pipeline execution (extract + submit)"""
    status: Literal["success", "partial", "failed"] = Field(..., description="Overall pipeline status")
    email_subject: Optional[str] = Field(None, description="Subject of processed email")
    orders_extracted: int = Field(0, description="Number of orders extracted")
    orders_submitted: int = Field(0, description="Number of orders successfully submitted")
    orders_failed: int = Field(0, description="Number of orders that failed")
    successful_orders: List[OrderResult] = Field(default_factory=list, description="Successfully submitted orders")
    failed_orders: List[OrderResult] = Field(default_factory=list, description="Failed order submissions")
    error: Optional[str] = Field(None, description="Error message if pipeline failed")
    stage: Optional[str] = Field(None, description="Pipeline stage where failure occurred (if failed)")

