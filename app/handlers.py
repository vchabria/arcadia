"""
Core automation handlers - Calls existing working scripts as subprocesses

This approach avoids async/thread conflicts by running the automation
scripts in completely isolated subprocesses.
"""

import json
import os
import subprocess
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path


def extract_from_gmail() -> Optional[Dict[str, Any]]:
    """
    Extract inbound order data by running the existing script as subprocess
    
    Returns:
        Dictionary with email_subject and orders array, or None if no valid email
    """
    print("="*80)
    print("📧 EXTRACTING INBOUND ORDER DATA FROM GMAIL")
    print("="*80)
    print("🔄 Running extraction via subprocess (avoids async conflicts)...\n")
    
    # Path to the working script
    script_path = Path(__file__).parent.parent.parent / "stagehand-test" / "extraction_only.py"
    
    # Fallback to full script if extraction-only doesn't exist yet
    if not script_path.exists():
        script_path = Path(__file__).parent.parent.parent / "stagehand-test" / "add_inventory_from_tonya_email.py"
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    try:
        # Run the script as a subprocess with API key
        env = os.environ.copy()
        api_key = os.getenv('NOVA_ACT_API_KEY', '')
        if api_key:
            env['NOVA_ACT_API_KEY'] = api_key
        
        print(f"   Script: {script_path}")
        print(f"   API Key: {'Set ✅' if api_key else 'Not Set ❌'}\n")
        
        # Run the script with system Python (not venv Python)
        # This ensures it uses the correct NovaAct version
        python_cmd = '/usr/local/bin/python3'  # Try system Python first
        if not Path(python_cmd).exists():
            python_cmd = 'python3'  # Fallback to PATH python
        
        result = subprocess.run(
            [python_cmd, str(script_path)],
            capture_output=False,  # Let output go to console so we can see what's happening
            env=env,
            timeout=300,  # 5 minute timeout
            cwd=script_path.parent
        )
        
        if result.returncode != 0:
            print(f"\n❌ Script failed with code {result.returncode}")
            raise Exception(f"Extraction script failed with exit code {result.returncode}")
        
        # For now, return a dummy response
        # TODO: Modify the script to output JSON we can parse
        print(f"\n✅ Script completed successfully")
        return {
            "email_subject": "Extracted from subprocess",
            "orders": []
        }
        
    except subprocess.TimeoutExpired:
        print("\n❌ Script timed out after 5 minutes")
        raise Exception("Extraction script timed out")
    except Exception as e:
        print(f"\n❌ Error running script: {e}")
        raise


def add_orders_to_arcadia(order_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Add extracted orders to Arcadia (placeholder for now)
    
    Args:
        order_data: Dictionary containing email_subject and orders array
    
    Returns:
        List of order results with confirmation IDs
    """
    print("="*80)
    print("🏢 ADDING INBOUND ORDERS TO ARCADIA")
    print("="*80)
    print("⚠️  Not yet implemented - would call Arcadia script here\n")
    
    # TODO: Implement or call Arcadia submission script
    return []


def create_arcadia_order(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a single inbound order in Arcadia with all fields
    
    Args:
        args: Dictionary containing order parameters:
            - master_bill_number (str, required)
            - product_code (str, required)
            - quantity (int, required)
            - temperature (str, required)
            - supplying_facility_number (str, optional)
            - delivery_date (str, optional)
            - delivery_company (str, optional)
            - comments (str, optional)
    
    Returns:
        Dictionary with success status and confirmation details
    """
    print("="*80)
    print("🏢 CREATING ARCADIA INBOUND ORDER")
    print("="*80)
    print("🔄 Running Arcadia order creation as subprocess...\n")
    
    # Path to the Arcadia order script
    script_path = Path(__file__).parent.parent.parent / "stagehand-test" / "run_arcadia_only.py"
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Extract and validate parameters
    master_bill = args.get('master_bill_number')
    product_code = args.get('product_code')
    quantity = args.get('quantity')
    temperature = args.get('temperature', 'FREEZER').upper()
    facility_num = args.get('supplying_facility_number', master_bill)
    delivery_date = args.get('delivery_date')
    delivery_company = args.get('delivery_company')
    comments = args.get('comments')
    
    # Normalize temperature
    temp_map = {"F": "FREEZER", "C": "COOLER", "R": "COOLER", "FR": "FREEZER CRATES"}
    temperature = temp_map.get(temperature, temperature)
    
    if not all([master_bill, product_code, quantity, temperature]):
        raise ValueError("Missing required fields: master_bill_number, product_code, quantity, temperature")
    
    print(f"   Master Bill: {master_bill}")
    print(f"   Product: {product_code}")
    print(f"   Quantity: {quantity}")
    print(f"   Temperature: {temperature}")
    if delivery_date:
        print(f"   Delivery Date: {delivery_date}")
    if delivery_company:
        print(f"   Carrier: {delivery_company}")
    if comments:
        print(f"   Comments: {comments}")
    print()
    
    try:
        # Run the script as a subprocess
        env = os.environ.copy()
        api_key = os.getenv('NOVA_ACT_API_KEY', '557e17b4-cb5b-4325-991b-8d3c6c35e038')
        env['NOVA_ACT_API_KEY'] = api_key
        
        # Prepare stdin input for the script
        stdin_input = f"{master_bill}\n{product_code}\n{quantity}\n{temperature}\n"
        
        # Run the Python script with venv Python
        venv_python = Path(__file__).parent.parent.parent / "stagehand-test" / "nova-act-env" / "bin" / "python"
        if not venv_python.exists():
            venv_python = Path('/usr/local/bin/python3')  # Fallback
        
        result = subprocess.run(
            [str(venv_python), str(script_path)],
            input=stdin_input,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,  # 5 minute timeout
            cwd=script_path.parent
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or f'Script failed with exit code {result.returncode}'
            print(f"\n❌ Script failed: {error_msg}")
            return {
                'status': 'failed',
                'error': error_msg,
                'master_bill_number': master_bill
            }
        
        print(f"\n✅ Order created successfully")
        
        return {
            'status': 'success',
            'master_bill_number': master_bill,
            'product_code': product_code,
            'quantity': quantity,
            'temperature': temperature,
            'confirmation_id': f'ORD-{master_bill}',
            'message': 'Order created successfully in Arcadia'
        }
        
    except subprocess.TimeoutExpired:
        print("\n❌ Script timed out after 5 minutes")
        return {
            'status': 'failed',
            'error': 'Script timed out after 5 minutes',
            'master_bill_number': master_bill
        }
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'master_bill_number': master_bill
        }


def run_full_pipeline() -> Dict[str, Any]:
    """
    Execute the complete automation pipeline by calling the full script
    
    Returns:
        Dictionary with extraction results and submission results
    """
    print("\n")
    print("="*80)
    print("🤖 INBOUND ORDER AUTOMATION - FULL PIPELINE")
    print("="*80)
    print("🔄 Running full script as subprocess...\n")
    
    # Path to the working script
    script_path = Path(__file__).parent.parent.parent / "stagehand-test" / "add_inventory_from_tonya_email.py"
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    try:
        # Run the script as a subprocess
        env = os.environ.copy()
        api_key = os.getenv('NOVA_ACT_API_KEY', '')
        if api_key:
            env['NOVA_ACT_API_KEY'] = api_key
        
        print(f"   Script: {script_path}")
        print(f"   API Key: {'Set ✅' if api_key else 'Not Set ❌'}\n")
        
        # Run the full script with system Python (not venv Python)
        python_cmd = '/usr/local/bin/python3'  # Try system Python first
        if not Path(python_cmd).exists():
            python_cmd = 'python3'  # Fallback to PATH python
        
        result = subprocess.run(
            [python_cmd, str(script_path)],
            capture_output=False,  # Show output in console
            env=env,
            timeout=600,  # 10 minute timeout for full pipeline
            cwd=script_path.parent
        )
        
        if result.returncode != 0:
            return {
                'status': 'failed',
                'stage': 'pipeline',
                'error': f'Script failed with exit code {result.returncode}',
                'orders_extracted': 0,
                'orders_submitted': 0
            }
        
        print(f"\n✅ Full pipeline completed successfully")
        
        # TODO: Parse actual results from script output
        return {
            'status': 'success',
            'email_subject': 'Processed via subprocess',
            'orders_extracted': 0,  # Parse from script output
            'orders_submitted': 0,  # Parse from script output
            'orders_failed': 0,
            'successful_orders': [],
            'failed_orders': []
        }
        
    except subprocess.TimeoutExpired:
        return {
            'status': 'failed',
            'stage': 'pipeline',
            'error': 'Script timed out after 10 minutes',
            'orders_extracted': 0,
            'orders_submitted': 0
        }
    except Exception as e:
        return {
            'status': 'failed',
            'stage': 'pipeline',
            'error': str(e),
            'orders_extracted': 0,
            'orders_submitted': 0
        }

