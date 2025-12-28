"""
Core business logic for inbound order automation

All functions are pure Python with no MCP, FastAPI, or HTTP dependencies.
Uses subprocess for script execution to avoid async conflicts with NovaAct.
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any

from .schemas import (
    EmailExtractionData,
    OrderData,
    CreateOrderInput,
    OrderResult,
    ExtractionResult,
    SubmissionResult,
    PipelineResult,
)
from .errors import (
    ExtractionError,
    SubmissionError,
    ScriptExecutionError,
    TimeoutError as AutomationTimeoutError,
    ValidationError,
)


def extract_orders_from_gmail() -> ExtractionResult:
    """
    Extract inbound order data from Gmail by running extraction script
    
    Returns:
        ExtractionResult with email_subject and orders array
    
    Raises:
        ExtractionError: If extraction fails
        AutomationTimeoutError: If script times out
    """
    print("=" * 80)
    print("📧 EXTRACTING INBOUND ORDER DATA FROM GMAIL")
    print("=" * 80)
    print("🔄 Running extraction via subprocess (avoids async conflicts)...\n")
    
    # Path to the working script (relative to this file)
    script_path = Path(__file__).parent.parent.parent / "stagehand-test" / "extraction_only.py"
    
    # Fallback to full script if extraction-only doesn't exist
    if not script_path.exists():
        script_path = Path(__file__).parent.parent.parent / "stagehand-test" / "add_inventory_from_tonya_email.py"
    
    if not script_path.exists():
        raise ExtractionError(f"Extraction script not found: {script_path}")
    
    try:
        # Prepare environment with API key
        env = os.environ.copy()
        api_key = os.getenv('NOVA_ACT_API_KEY')
        
        if not api_key:
            print("   ⚠️  WARNING: NOVA_ACT_API_KEY not set - extraction may fail")
        else:
            env['NOVA_ACT_API_KEY'] = api_key
        
        print(f"   Script: {script_path}")
        print(f"   API Key: {'Set ✅' if api_key else 'Not Set ❌'}\n")
        
        # Determine Python command
        python_cmd = _get_python_command()
        
        # Run the script as subprocess
        result = subprocess.run(
            [python_cmd, str(script_path)],
            capture_output=True,
            text=True,
            env=env,
            timeout=300,  # 5 minute timeout
            cwd=script_path.parent
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or f'Script failed with exit code {result.returncode}'
            print(f"\n❌ Script failed: {error_msg}")
            raise ScriptExecutionError(
                f"Extraction script failed: {error_msg}",
                exit_code=result.returncode,
                stderr=result.stderr
            )
        
        print(f"\n✅ Extraction completed successfully")
        
        # TODO: Parse actual JSON output from script
        # For now, return a placeholder response
        return ExtractionResult(
            status="success",
            email_subject="Extracted from subprocess",
            orders_count=0,
            orders=[]
        )
        
    except subprocess.TimeoutExpired:
        print("\n❌ Script timed out after 5 minutes")
        raise AutomationTimeoutError("Extraction script timed out", timeout_seconds=300)
    except (ExtractionError, AutomationTimeoutError, ScriptExecutionError):
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error during extraction: {e}")
        raise ExtractionError(f"Extraction failed: {str(e)}") from e


def submit_orders_to_arcadia(email_data: EmailExtractionData) -> SubmissionResult:
    """
    Submit extracted orders to Arcadia
    
    Args:
        email_data: EmailExtractionData with orders to submit
    
    Returns:
        SubmissionResult with submission status and results
    
    Raises:
        SubmissionError: If submission fails
    """
    print("=" * 80)
    print("🏢 SUBMITTING ORDERS TO ARCADIA")
    print("=" * 80)
    print(f"📧 Email: {email_data.email_subject}")
    print(f"📦 Orders to submit: {len(email_data.orders)}\n")
    
    if not email_data.orders:
        raise ValidationError("No orders to submit")
    
    successful_orders = []
    failed_orders = []
    
    # Submit each order individually
    for order in email_data.orders:
        for product in order.products:
            try:
                # Create order input
                order_input = CreateOrderInput(
                    master_bill_number=order.master_bill_number,
                    product_code=product.product_code,
                    quantity=product.quantity,
                    temperature=product.temperature,
                    supplying_facility_number=order.supplying_facility_number or order.master_bill_number,
                    delivery_date=order.date,
                )
                
                # Submit single order
                result = create_single_arcadia_order(order_input)
                
                if result.status == "success":
                    successful_orders.append(result)
                else:
                    failed_orders.append(result)
                    
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Failed to submit {product.product_code}: {error_msg}")
                failed_orders.append(
                    OrderResult(
                        status="failed",
                        master_bill_number=order.master_bill_number,
                        product_code=product.product_code,
                        quantity=product.quantity,
                        error=error_msg
                    )
                )
    
    # Determine overall status
    if not failed_orders:
        status = "success"
    elif successful_orders:
        status = "partial"
    else:
        status = "failed"
    
    return SubmissionResult(
        status=status,
        orders_submitted=len(successful_orders),
        orders_failed=len(failed_orders),
        successful_orders=successful_orders,
        failed_orders=failed_orders
    )


def create_single_arcadia_order(order_input: CreateOrderInput) -> OrderResult:
    """
    Create a single inbound order in Arcadia with all fields
    
    Args:
        order_input: CreateOrderInput with order parameters
    
    Returns:
        OrderResult with submission status
    
    Raises:
        ValidationError: If input validation fails
        ScriptExecutionError: If script execution fails
        AutomationTimeoutError: If script times out
    """
    print("=" * 80)
    print("🏢 CREATING ARCADIA INBOUND ORDER")
    print("=" * 80)
    print("🔄 Running Arcadia order creation as subprocess...\n")
    
    # Path to the Arcadia order script (now inside inbound_mcp/scripts/)
    script_path = Path(__file__).parent.parent / "scripts" / "run_arcadia_only.py"
    
    if not script_path.exists():
        raise ScriptExecutionError(f"Arcadia script not found: {script_path}")
    
    # Extract parameters
    master_bill = order_input.master_bill_number
    product_code = order_input.product_code
    quantity = order_input.quantity
    temperature = order_input.temperature
    facility_num = order_input.supplying_facility_number or master_bill
    
    print(f"   Master Bill: {master_bill}")
    print(f"   Product: {product_code}")
    print(f"   Quantity: {quantity}")
    print(f"   Temperature: {temperature}")
    if order_input.delivery_date:
        print(f"   Delivery Date: {order_input.delivery_date}")
    if order_input.delivery_company:
        print(f"   Carrier: {order_input.delivery_company}")
    if order_input.comments:
        print(f"   Comments: {order_input.comments}")
    print()
    
    try:
        # Prepare environment
        env = os.environ.copy()
        api_key = os.getenv('NOVA_ACT_API_KEY')
        
        if not api_key:
            raise ValidationError("NOVA_ACT_API_KEY environment variable is required")
        
        env['NOVA_ACT_API_KEY'] = api_key
        
        # Pass Arcadia credentials for auto-login (if set)
        arcadia_username = os.getenv('ARCADIA_USERNAME')
        arcadia_password = os.getenv('ARCADIA_PASSWORD')
        if arcadia_username:
            env['ARCADIA_USERNAME'] = arcadia_username
        if arcadia_password:
            env['ARCADIA_PASSWORD'] = arcadia_password
        
        # Get Python command - use system Python in production
        python_cmd = _get_python_command()
        
        # Prepare command with all arguments
        cmd_args = [python_cmd, str(script_path), master_bill, product_code, str(quantity), temperature]
        
        # Add optional fields if provided
        if order_input.delivery_date:
            cmd_args.append(order_input.delivery_date)
        else:
            cmd_args.append("")  # Empty placeholder
            
        if order_input.delivery_company:
            cmd_args.append(order_input.delivery_company)
        else:
            cmd_args.append("")  # Empty placeholder
            
        if order_input.comments:
            cmd_args.append(order_input.comments)
        else:
            cmd_args.append("")  # Empty placeholder
        
        print(f"   Command: {' '.join(cmd_args)}\n")
        
        # Run the script with command-line arguments
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,  # 5 minute timeout
            cwd=script_path.parent
        )
        
        # Parse JSON output from script to extract video_path
        video_path = None
        try:
            # Look for JSON output in stdout
            import json
            import re
            json_match = re.search(r'\{[\s\S]*"success"[\s\S]*\}', result.stdout)
            if json_match:
                script_result = json.loads(json_match.group())
                video_path = script_result.get('video_path')
                if video_path:
                    print(f"\n🎥 Video recorded: {video_path}")
        except Exception as e:
            print(f"⚠️  Could not parse video path from output: {e}")
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or f'Script failed with exit code {result.returncode}'
            print(f"\n❌ Script failed: {error_msg}")
            return OrderResult(
                status="failed",
                master_bill_number=master_bill,
                product_code=product_code,
                quantity=quantity,
                temperature=temperature,
                error=error_msg,
                video_path=video_path
            )
        
        print(f"\n✅ Order created successfully")
        
        return OrderResult(
            status="success",
            master_bill_number=master_bill,
            product_code=product_code,
            quantity=quantity,
            temperature=temperature,
            confirmation_id=f'ORD-{master_bill}',
            message='Order created successfully in Arcadia',
            video_path=video_path
        )
        
    except subprocess.TimeoutExpired as e:
        print("\n❌ Script timed out after 5 minutes")
        # Try to get video_path even on timeout
        video_path = None
        try:
            import json
            import re
            if hasattr(e, 'stdout') and e.stdout:
                json_match = re.search(r'\{[\s\S]*"video_path"[\s\S]*\}', e.stdout)
                if json_match:
                    script_result = json.loads(json_match.group())
                    video_path = script_result.get('video_path')
        except:
            pass
        
        return OrderResult(
            status="failed",
            master_bill_number=master_bill,
            product_code=product_code,
            quantity=quantity,
            error='Script timed out after 5 minutes',
            video_path=video_path
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return OrderResult(
            status="failed",
            master_bill_number=master_bill,
            product_code=product_code,
            quantity=quantity,
            error=str(e)
        )


def run_complete_pipeline() -> PipelineResult:
    """
    Execute the complete automation pipeline (extract + submit)
    
    Returns:
        PipelineResult with extraction and submission results
    
    Raises:
        ExtractionError: If extraction fails
        SubmissionError: If submission fails
    """
    print("\n")
    print("=" * 80)
    print("🤖 INBOUND ORDER AUTOMATION - FULL PIPELINE")
    print("=" * 80)
    print("🔄 Step 1: Extracting from Gmail...")
    print()
    
    try:
        # Step 1: Extract orders from Gmail
        extraction_result = extract_orders_from_gmail()
        
        if extraction_result.status != "success" or not extraction_result.orders:
            return PipelineResult(
                status="failed",
                stage="extraction",
                error=extraction_result.error or "No orders extracted",
                orders_extracted=0,
                orders_submitted=0,
                orders_failed=0
            )
        
        print(f"\n✅ Extracted {extraction_result.orders_count} orders")
        print("\n🔄 Step 2: Submitting to Arcadia...")
        print()
        
        # Step 2: Submit to Arcadia
        email_data = EmailExtractionData(
            email_subject=extraction_result.email_subject or "Unknown",
            orders=extraction_result.orders
        )
        
        submission_result = submit_orders_to_arcadia(email_data)
        
        # Determine overall status
        if submission_result.status == "success":
            status = "success"
        elif submission_result.status == "partial":
            status = "partial"
        else:
            status = "failed"
        
        return PipelineResult(
            status=status,
            email_subject=extraction_result.email_subject,
            orders_extracted=extraction_result.orders_count,
            orders_submitted=submission_result.orders_submitted,
            orders_failed=submission_result.orders_failed,
            successful_orders=submission_result.successful_orders,
            failed_orders=submission_result.failed_orders
        )
        
    except ExtractionError as e:
        return PipelineResult(
            status="failed",
            stage="extraction",
            error=str(e),
            orders_extracted=0,
            orders_submitted=0,
            orders_failed=0
        )
    except SubmissionError as e:
        return PipelineResult(
            status="failed",
            stage="submission",
            error=str(e),
            orders_extracted=0,
            orders_submitted=0,
            orders_failed=0
        )
    except Exception as e:
        return PipelineResult(
            status="failed",
            stage="unknown",
            error=str(e),
            orders_extracted=0,
            orders_submitted=0,
            orders_failed=0
        )


def _get_python_command() -> str:
    """
    Determine the best Python command to use
    
    Returns:
        Path to Python executable
    """
    # Try system Python first
    system_python = '/usr/local/bin/python3'
    if Path(system_python).exists():
        return system_python
    
    # Fallback to PATH python
    return 'python3'

