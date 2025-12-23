"""
Core automation handlers for Gmail extraction and Arcadia submission

These handlers wrap the NovaAct automation logic and return structured data
for the MCP endpoints.
"""

import json
import os
import time
import subprocess
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path


def extract_from_gmail() -> Optional[Dict[str, Any]]:
    """
    Extract inbound order data from Arjun's Gmail emails by calling the working script
    
    This runs the existing add_inventory_from_tonya_email.py script as a subprocess
    to avoid async/thread conflicts with NovaAct.
    
    Returns:
        Dictionary with email_subject and orders array, or None if no valid email
    """
    print("="*80)
    print("📧 EXTRACTING INBOUND ORDER DATA FROM GMAIL")
    print("="*80)
    print("🔄 Running extraction script as subprocess...\n")
    
    # Path to the working script
    script_path = Path(__file__).parent.parent.parent / "stagehand-test" / "add_inventory_from_tonya_email.py"
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    try:
        # Run the script as a subprocess with API key
        env = os.environ.copy()
        env['NOVA_ACT_API_KEY'] = os.getenv('NOVA_ACT_API_KEY', '')
        
        # Run in extraction-only mode (we'll modify the script to support this)
        result = subprocess.run(
            [sys.executable, str(script_path), '--extract-only'],
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"❌ Script failed with code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            raise Exception(f"Extraction script failed: {result.stderr}")
        
        # Parse the output JSON
        try:
            output_data = json.loads(result.stdout)
            print(f"✅ Extracted {len(output_data.get('orders', []))} orders\n")
            return output_data
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse script output: {e}")
            print(f"STDOUT: {result.stdout}")
            raise Exception(f"Failed to parse extraction output: {e}")
        
        # Search for emails from Arjun with inbound ATL keywords
        print("🔍 Searching for inbound ATL emails from Arjun...")
        nova.act("""
            Click the Gmail search box.
            Type: from:arjun@packaging-systems.com (inbound OR ATL OR pallets)
            Press Enter.
        """, max_steps=5)
        print("✅ Search complete\n")
        
        # Open most recent email
        print("📧 Opening most recent email...")
        nova.act("Click the first email in the search results", max_steps=2)
        print("✅ Email opened\n")
        
        # Check the subject line
        print("🔍 Checking email subject...")
        subject_check = nova.act("""
            Get the email subject line.
            Return the subject as a string.
        """, max_steps=2, schema={
            "type": "object",
            "properties": {
                "subject": {"type": "string"}
            }
        })
        
        # Parse subject
        subject_str = str(subject_check)
        subject = ""
        if "subject" in subject_str.lower():
            start_idx = subject_str.find('{')
            if start_idx != -1:
                brace_count = 0
                for i in range(start_idx, len(subject_str)):
                    if subject_str[i] == '{':
                        brace_count += 1
                    elif subject_str[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = subject_str[start_idx:i+1]
                            try:
                                subject_data = json.loads(json_str)
                                subject = subject_data.get('subject', '')
                            except:
                                subject = subject_str
                            break
        else:
            subject = subject_str
        
        print(f"   Subject: {subject}")
        
        # Check if subject contains "inbound" and "atl"
        if "inbound" not in subject.lower() or "atl" not in subject.lower():
            print("\n⚠️  Email subject does not contain 'inbound atl'")
            print("   Skipping this email.\n")
            return None
        
        print("✅ Subject contains 'inbound atl' - proceeding\n")
        
        # Extract order data
        print("📦 Extracting order data...")
        order_data = nova.act("""
            Extract all inbound orders from this email body.
            
            Look for the format:
            "6/9 Monday
            060920251 -PP48F – 24 pallets
            060920252-SPLIT LOAD -BTL18-1R – 18 pallets/ PP24F – 6 pallets"
            
            For each order line, extract:
            - Date (e.g., "6/9 Monday")
            - Master Bill Number (9 digit number, e.g., "060920251")
            - Product Code (5 alphanumeric after the dash, e.g., "PP48F", "BTL18-1R")
            - Quantity (number only, e.g., "24", "18")
            - Split load flag if "SPLIT LOAD" is mentioned
            
            IMPORTANT: 
            - Each 9-digit number is BOTH the master bill number AND supplying facilities number
            - Multiple products can be on one order (split load)
            - Group products by their master bill number
            
            Return all orders found.
        """, max_steps=10, schema={
            "type": "object",
            "properties": {
                "email_subject": {"type": "string"},
                "orders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "master_bill_number": {"type": "string"},
                            "supplying_facility_number": {"type": "string"},
                            "products": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "product_code": {"type": "string"},
                                        "quantity": {"type": "string"}
                                    }
                                }
                            },
                            "split_load": {"type": "boolean"}
                        }
                    }
                }
            }
        })
        
        # Parse the result
        result_str = str(order_data)
        start_idx = result_str.find('{')
        if start_idx != -1:
            brace_count = 0
            for i in range(start_idx, len(result_str)):
                if result_str[i] == '{':
                    brace_count += 1
                elif result_str[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_str = result_str[start_idx:i+1]
                        try:
                            order_data = json.loads(json_str)
                        except:
                            order_data = {}
                        break
        else:
            order_data = {}
        
        orders = order_data.get('orders', []) if isinstance(order_data, dict) else []
        email_subject = order_data.get('email_subject', subject) if isinstance(order_data, dict) else subject
        
        # Process orders and add temperature based on product code
        for order in orders:
            # Make sure supplying_facility_number matches master_bill_number
            if not order.get('supplying_facility_number'):
                order['supplying_facility_number'] = order.get('master_bill_number', '')
            
            # Add temperature to each product based on last character
            for product in order.get('products', []):
                product_code = product.get('product_code', '')
                temperature = parse_temperature_from_product_code(product_code)
                product['temperature'] = temperature
        
        print(f"✅ Extracted {len(orders)} inbound orders from: {email_subject}\n")
        
        for i, order in enumerate(orders, 1):
            print(f"   Order {i}:")
            print(f"      Date: {order.get('date')}")
            print(f"      Master Bill: {order.get('master_bill_number')}")
            print(f"      Supplying Facility: {order.get('supplying_facility_number')}")
            print(f"      Split Load: {order.get('split_load', False)}")
            for j, prod in enumerate(order.get('products', []), 1):
                print(f"         Product {j}: {prod.get('product_code')} - {prod.get('quantity')} pallets - {prod.get('temperature')}")
            print()
        
        return {
            'email_subject': email_subject,
            'orders': orders
        }
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        raise
        
    finally:
        print("🔚 Closing Gmail...")
        nova.stop()
        print("✅ Gmail closed\n")


def add_orders_to_arcadia(order_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Add extracted orders to Arcadia's Inbound Order system
    
    Args:
        order_data: Dictionary containing email_subject and orders array
    
    Returns:
        List of order results with confirmation IDs
    """
    
    if not order_data or not order_data.get('orders'):
        print("⚠️  No orders to add")
        return []
    
    orders = order_data['orders']
    
    print("="*80)
    print("🏢 ADDING INBOUND ORDERS TO ARCADIA")
    print("="*80)
    print(f"\n📋 Adding {len(orders)} inbound orders\n")
    
    nova = NovaAct(
        starting_page="https://arcadiaone.com/dashboard",
        user_data_dir="./contexts/arcadia_profile",
        clone_user_data_dir=True,
        headless=False,  # Show browser window so you can see what's happening
        screen_width=1600,
        screen_height=900
    )
    
    added_orders = []
    
    try:
        print("🌐 Opening Arcadia...")
        nova.start()
        print("✅ Arcadia opened\n")
        
        print("⏳ Waiting 5 seconds for page to fully load...")
        time.sleep(5)
        print()
        
        for idx, order in enumerate(orders, 1):
            print(f"📦 Processing Order {idx}/{len(orders)}")
            print(f"   Master Bill: {order.get('master_bill_number')}")
            print(f"   Date: {order.get('date')}")
            print(f"   Products: {len(order.get('products', []))}")
            print()
            
            try:
                # Navigate to Inbound Order page
                print("   → Navigating to Inbound Order page...")
                nova.act("""
                    Look for and click 'Inbound Order' link or button.
                    This might be in the main navigation, sidebar, or under Inventory menu.
                """, max_steps=5)
                print("   ✅ On Inbound Order page")
                print("   ⏳ Waiting 3 seconds...")
                time.sleep(3)
                print()
                
                # Check if we need to click "Add New" button
                print("   → Looking for 'Add New' or 'Create Order' button...")
                try:
                    nova.act("""
                        Look for and click:
                        - 'Add New' button
                        - 'Create Order' button
                        - 'New Order' button
                        - '+' button to add a new order
                        
                        If no such button exists and you see a blank form, skip this step.
                    """, max_steps=5)
                    print("   ✅ Clicked to create new order")
                    print("   ⏳ Waiting 2 seconds...")
                    time.sleep(2)
                except Exception:
                    print("   ℹ️  No 'Add New' button found, assuming form is ready")
                print()
                
                # Fill Master Bill Number
                master_bill = order.get('master_bill_number', '')
                print(f"   → Filling Master Bill Number: {master_bill}...")
                nova.act(f"""
                    Find the 'Master Bill Number' field or 'Master Bill' input box.
                    Click on it and enter: {master_bill}
                """, max_steps=5)
                print("   ✅ Master Bill Number entered")
                print("   ⏳ Waiting 2 seconds...")
                time.sleep(2)
                print()
                
                # Fill Supplying Facility Number
                facility_num = order.get('supplying_facility_number', master_bill)
                print(f"   → Filling Supplying Facility Number: {facility_num}...")
                nova.act(f"""
                    Find the 'Supplying Facility Number' or 'Facility Number' field.
                    Click on it and enter: {facility_num}
                """, max_steps=5)
                print("   ✅ Supplying Facility Number entered")
                print("   ⏳ Waiting 2 seconds...")
                time.sleep(2)
                print()
                
                # Fill Date if available
                if order.get('date'):
                    print(f"   → Filling Date: {order.get('date')}...")
                    nova.act(f"""
                        If there's a Date field or Delivery Date field, click on it and enter: {order.get('date')}
                        If no such field exists, skip this step.
                    """, max_steps=3)
                    print("   ✅ Date entered")
                    print("   ⏳ Waiting 2 seconds...")
                    time.sleep(2)
                    print()
                
                # Add each product
                products = order.get('products', [])
                for prod_idx, product in enumerate(products, 1):
                    product_code = product.get('product_code', '')
                    quantity = product.get('quantity', '')
                    temperature = product.get('temperature', 'FREEZER')
                    
                    print(f"   → Adding Product {prod_idx}/{len(products)}: {product_code}")
                    print("   ⏳ Waiting 1 second...")
                    time.sleep(1)
                    
                    # Fill Product Code
                    nova.act(f"""
                        Find the Product Code field or Product dropdown.
                        Click on it and enter or select: {product_code}
                    """, max_steps=5)
                    print(f"      ✅ Product code: {product_code}")
                    print("      ⏳ Waiting 2 seconds...")
                    time.sleep(2)
                    
                    # Fill Quantity
                    nova.act(f"""
                        Find the Quantity field.
                        Click on it and enter: {quantity}
                    """, max_steps=4)
                    print(f"      ✅ Quantity: {quantity}")
                    print("      ⏳ Waiting 2 seconds...")
                    time.sleep(2)
                    
                    # Select Temperature
                    print(f"      → Selecting temperature: {temperature}")
                    nova.act(f"""
                        Find the Temperature dropdown or selector.
                        Click to open it.
                        Select the option for: {temperature}
                        
                        Options might be:
                        - FREEZER or Freezer
                        - COOLER or Cooler
                        - FREEZER CRATES or Freezer Crates
                    """, max_steps=6)
                    print(f"      ✅ Temperature: {temperature}")
                    print("      ⏳ Waiting 2 seconds...")
                    time.sleep(2)
                    
                    # Add another product line if needed
                    if prod_idx < len(products):
                        print(f"      → Adding another product line...")
                        nova.act("""
                            If there's an 'Add Product' or 'Add Line' or '+' button to add another product, click it.
                            Otherwise, continue to the next field.
                        """, max_steps=3)
                        print("      ⏳ Waiting 2 seconds...")
                        time.sleep(2)
                    
                    print()
                
                # Submit the order
                print("   → Submitting inbound order...")
                print("   ⏳ Waiting 2 seconds before submission...")
                time.sleep(2)
                submission_result = nova.act("""
                    Click the Submit, Save, or Add button to create the inbound order.
                    After submission, look for a confirmation message or order ID.
                    Return any confirmation number or order ID shown.
                """, max_steps=6, schema={
                    "type": "object",
                    "properties": {
                        "confirmation_id": {"type": "string"},
                        "success": {"type": "boolean"}
                    }
                })
                
                # Parse confirmation
                conf_str = str(submission_result)
                confirmation_id = None
                if '{' in conf_str:
                    start_idx = conf_str.find('{')
                    brace_count = 0
                    for i in range(start_idx, len(conf_str)):
                        if conf_str[i] == '{':
                            brace_count += 1
                        elif conf_str[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_str = conf_str[start_idx:i+1]
                                try:
                                    conf_data = json.loads(json_str)
                                    confirmation_id = conf_data.get('confirmation_id')
                                except:
                                    pass
                                break
                
                if not confirmation_id:
                    confirmation_id = f"ORD-{master_bill}"
                
                print(f"   ✅ Order submitted! ID: {confirmation_id}\n")
                
                added_orders.append({
                    'master_bill_number': master_bill,
                    'confirmation_id': confirmation_id,
                    'products': products,
                    'status': 'success'
                })
                
                # Go back to dashboard for next order
                if idx < len(orders):
                    print("   → Returning to dashboard for next order...")
                    nova.act("Click 'Dashboard'", max_steps=2)
                    print()
                
            except Exception as e:
                print(f"   ❌ Error adding order: {e}\n")
                added_orders.append({
                    'master_bill_number': order.get('master_bill_number'),
                    'confirmation_id': None,
                    'products': order.get('products', []),
                    'status': 'failed',
                    'error': str(e)
                })
                
                # Try to go back to dashboard
                try:
                    nova.act("Click 'Dashboard'", max_steps=2)
                except:
                    pass
        
        return added_orders
        
    except Exception as e:
        print(f"❌ Critical error: {e}\n")
        import traceback
        traceback.print_exc()
        return added_orders
        
    finally:
        print("🔚 Closing Arcadia...")
        nova.stop()
        print("✅ Arcadia closed\n")


def run_full_pipeline() -> Dict[str, Any]:
    """
    Execute the complete automation pipeline
    
    Workflow:
    1. Extract orders from Gmail
    2. Add orders to Arcadia
    3. Return summary with confirmation IDs
    
    Returns:
        Dictionary with extraction results and submission results
    """
    print("\n")
    print("="*80)
    print("🤖 INBOUND ORDER AUTOMATION - FULL PIPELINE")
    print("="*80)
    print()
    
    # Step 1: Extract from Gmail
    try:
        order_data = extract_from_gmail()
    except Exception as e:
        return {
            'status': 'failed',
            'stage': 'extraction',
            'error': str(e),
            'orders_extracted': 0,
            'orders_submitted': 0
        }
    
    if not order_data:
        return {
            'status': 'failed',
            'stage': 'extraction',
            'error': 'No valid inbound ATL email found',
            'orders_extracted': 0,
            'orders_submitted': 0
        }
    
    # Step 2: Add orders to Arcadia
    try:
        results = add_orders_to_arcadia(order_data)
    except Exception as e:
        return {
            'status': 'partial',
            'stage': 'submission',
            'error': str(e),
            'email_subject': order_data.get('email_subject'),
            'orders_extracted': len(order_data.get('orders', [])),
            'orders_submitted': 0,
            'extracted_orders': order_data.get('orders', [])
        }
    
    # Build summary
    successful = [r for r in results if r.get('status') == 'success']
    failed = [r for r in results if r.get('status') == 'failed']
    
    return {
        'status': 'success' if not failed else 'partial',
        'email_subject': order_data.get('email_subject'),
        'orders_extracted': len(order_data.get('orders', [])),
        'orders_submitted': len(successful),
        'orders_failed': len(failed),
        'successful_orders': successful,
        'failed_orders': failed
    }

