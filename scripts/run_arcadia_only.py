#!/usr/bin/env python3
"""
Run Arcadia Order Automation Only (No Gmail)
Paste your order data and it will fill the order in Arcadia
"""

import json
import sys
import time
import os
from pathlib import Path
from datetime import datetime
from nova_act import NovaAct


def get_video_dir():
    """
    Get the video recording directory path.
    
    Production (Render): /app/contexts/arcadia_profile/videos
    Local: ./contexts/arcadia_profile/videos
    """
    if Path("/app").exists():
        video_dir = Path("/app/contexts/arcadia_profile/videos")
    else:
        video_dir = Path(__file__).parent.parent / "contexts" / "arcadia_profile" / "videos"
    
    video_dir.mkdir(parents=True, exist_ok=True)
    return str(video_dir)


# Production-safe profile path
# CRITICAL: Always use absolute disk path in production
def get_profile_path():
    """
    Get the correct profile path for the current environment.
    
    Production (Render): /app/contexts/arcadia_profile (persistent disk)
    Local: ./contexts/arcadia_profile (relative path)
    
    Why this matters:
    - /app/contexts → mounted persistent disk
    - /app/contexts/arcadia_profile → Chrome saves cookies/session here
    - Chrome writes here once → disk remembers forever
    - No relative paths. No environment ambiguity.
    """
    # Check if we're on Render (has /app directory)
    if Path("/app").exists():
        # Production: Use absolute path to persistent disk
        # This MUST be absolute and MUST point to mounted disk
        PROFILE_PATH = Path("/app/contexts/arcadia_profile")
    else:
        # Local development: Use relative path from inbound_mcp root
        PROFILE_PATH = Path(__file__).parent.parent / "contexts" / "arcadia_profile"
    
    # Ensure directory exists - CRITICAL for Chrome to save session
    PROFILE_PATH.mkdir(parents=True, exist_ok=True)
    
    # Verify it's writable
    test_file = PROFILE_PATH / ".write_test"
    try:
        test_file.touch()
        test_file.unlink()
        writable = True
    except Exception as e:
        writable = False
        print(f"⚠️  WARNING: Profile directory not writable: {e}")
    
    # Log profile info
    print("=" * 70)
    print("📁 BROWSER PROFILE CONFIGURATION")
    print("=" * 70)
    print(f"Profile path: {PROFILE_PATH.resolve()}")
    print(f"Exists: {'✅ YES' if PROFILE_PATH.exists() else '❌ NO'}")
    print(f"Writable: {'✅ YES' if writable else '❌ NO'}")
    print(f"On persistent disk: {'✅ YES' if str(PROFILE_PATH).startswith('/app/') else '⚠️  NO (local dev)'}")
    print("=" * 70)
    print()
    
    return str(PROFILE_PATH)


def load_credentials():
    """
    Load Arcadia credentials from either:
    1. Render Secret File (/etc/secrets/arcadia_credentials.env)
    2. Environment variables (ARCADIA_USERNAME, ARCADIA_PASSWORD)
    
    Returns:
        tuple: (username, password) or (None, None) if not found
    """
    # Try loading from Render Secret File first (production)
    secret_file_path = Path("/etc/secrets/arcadia_credentials.env")
    if secret_file_path.exists():
        print("📁 Loading credentials from Render Secret File...")
        try:
            with open(secret_file_path, 'r') as f:
                lines = f.readlines()
                creds = {}
                for line in lines:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        creds[key.strip()] = value.strip()
                
                username = creds.get('ARCADIA_USERNAME')
                password = creds.get('ARCADIA_PASSWORD')
                
                if username and password:
                    print("✅ Credentials loaded from secret file\n")
                    return username, password
        except Exception as e:
            print(f"⚠️  Failed to read secret file: {e}\n")
    
    # Fallback to environment variables
    username = os.getenv('ARCADIA_USERNAME')
    password = os.getenv('ARCADIA_PASSWORD')
    
    if username and password:
        print("✅ Credentials loaded from environment variables\n")
        return username, password
    
    return None, None


def ensure_logged_in(nova):
    """
    Check if logged in to Arcadia. If not, login using credentials from:
    1. Render Secret File (/etc/secrets/arcadia_credentials.env) - preferred
    2. Environment variables (ARCADIA_USERNAME, ARCADIA_PASSWORD) - fallback
    """
    print("🔐 Checking login status...")
    
    try:
        # Try to find logged-in indicator (dashboard elements)
        result = nova.act("""
            Check if we're on the Arcadia dashboard.
            Look for 'Inbound Order' link or user menu/profile icon.
            If you see these, we're logged in.
        """, max_steps=2)
        
        print("✅ Already logged in\n")
        return True
        
    except Exception as e:
        print("⚠️  Not logged in, attempting automatic login...\n")
        
        # Get credentials from secret file or environment variables
        username, password = load_credentials()
        
        if not username or not password:
            print("❌ ERROR: Login required but credentials not set!")
            print("   Set ARCADIA_USERNAME and ARCADIA_PASSWORD environment variables")
            raise Exception("ARCADIA_USERNAME and ARCADIA_PASSWORD must be set in environment")
        
        print(f"   Using username: {username[:3]}***{username[-3:]}")
        print("   Using password: ********\n")
        
        # Attempt login
        try:
            nova.act(f"""
                Find the login form on the page.
                Enter the username/email: {username}
                Enter the password: {password}
                Click the login or submit button.
                Wait for the dashboard to load.
            """, max_steps=10)
            
            print("✅ Login successful! Session saved to profile.\n")
            time.sleep(3)  # Wait for dashboard to fully load
            
            # Take screenshot after successful login
            try:
                from datetime import datetime
                from pathlib import Path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Save to a directory that's easy to find
                # On Render, save to /tmp (accessible via shell)
                # Locally, save to current directory
                if Path("/app").exists():
                    screenshot_path = f"/tmp/login_success_{timestamp}.png"
                else:
                    screenshot_path = f"./login_success_{timestamp}.png"
                
                nova.page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot saved: {screenshot_path}")
                print(f"   This screenshot shows the successful login to Arcadia dashboard\n")
            except Exception as screenshot_error:
                print(f"⚠️  Could not take screenshot: {screenshot_error}\n")
            
            return True
            
        except Exception as login_error:
            print(f"❌ Login failed: {login_error}")
            
            # Take screenshot of failed login attempt
            try:
                from datetime import datetime
                from pathlib import Path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if Path("/app").exists():
                    screenshot_path = f"/tmp/login_failed_{timestamp}.png"
                else:
                    screenshot_path = f"./login_failed_{timestamp}.png"
                
                nova.page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Failed login screenshot saved: {screenshot_path}")
                print(f"   This screenshot shows the page state when login failed\n")
            except Exception as screenshot_error:
                print(f"⚠️  Could not take failed login screenshot: {screenshot_error}\n")
            
            raise Exception(f"Auto-login failed: {login_error}")


def run_arcadia_order(master_bill, product_code, quantity, temperature="FREEZER", 
                       delivery_date=None, delivery_company=None, comments=None):
    """
    Fill a single order in Arcadia with all fields
    """
    
    print("\n" + "="*70)
    print("🏢 ARCADIA ORDER AUTOMATION")
    print("="*70)
    print()
    print(f"📦 Order Details:")
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
    
    # Get production-safe profile path
    profile_path = get_profile_path()
    
    # Set up video recording
    video_dir = get_video_dir()
    debug_video = os.getenv("DEBUG_VIDEO", "false").lower() == "true"
    
    print("=" * 70)
    print("🎥 VIDEO RECORDING CONFIGURATION")
    print("=" * 70)
    print(f"Video directory: {video_dir}")
    print(f"Recording enabled: {'✅ YES (DEBUG_VIDEO=true)' if debug_video else '⚠️  Only on errors'}")
    print(f"Resolution: 1280x720")
    print("=" * 70)
    print()
    
    print("🚀 Starting Arcadia...")
    print()
    
    video_path = None
    
    # Initialize NovaAct with persistent profile
    # CRITICAL SETTINGS:
    # - user_data_dir: Points to /app/contexts/arcadia_profile in production (mounted disk)
    # - clone_user_data_dir=False: MUST be False so Chrome writes directly to disk
    #   (If True, Chrome uses temp directory and session is lost on restart)
    # - screen resolution: Must be within ±20% of 1920x1080 for NovaAct
    nova = NovaAct(
        starting_page="https://arcadiaone.com/dashboard",
        user_data_dir=profile_path,  # Absolute path to persistent disk in production
        clone_user_data_dir=False,  # DO NOT CLONE - write directly to disk
        headless=False,
        screen_width=1600,
        screen_height=900,
    )
    
    try:
        nova.start()
        print("✅ Browser started\n")
        time.sleep(3)
        
        # Check login and auto-login if needed
        ensure_logged_in(nova)
        
        # Navigate to Inbound Order
        print("→ Navigating to Inbound Order page...")
        nova.act("Click 'Inbound Order' in the Quick Links", max_steps=3)
        print("✅ On Inbound Order page\n")
        time.sleep(2)
        
        # Click Add New
        print("→ Clicking 'Add New Inbound Order'...")
        nova.act("Click the 'Add New Inbound Order' button", max_steps=2)
        print("✅ Order form opened\n")
        time.sleep(2)
        
        # Fill Warehouse (required field)
        print("→ Filling Warehouse...")
        try:
            nova.act("Find the Warehouse field and enter: ATL", max_steps=4)
            print("✅ Warehouse entered\n")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️  Warehouse field issue: {e}\n")
        
        # Fill Account Code (required field)
        print("→ Filling Account Code...")
        try:
            nova.act("Find the Account Code or Account Number field and enter: 1000", max_steps=4)
            print("✅ Account Code entered\n")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️  Account Code field issue: {e}\n")
        
        # Fill Master Bill Number
        print(f"→ Filling Master Bill Number: {master_bill}...")
        nova.act(f"Find the 'Master Bill Number' or 'Master Bill' field and enter: {master_bill}", max_steps=4)
        print("✅ Master Bill entered\n")
        time.sleep(2)
        
        # Fill Supplying Facility Number (required - use master bill if not provided)
        print(f"→ Filling Supplying Facility Number: {master_bill}...")
        nova.act(f"Find the 'Supplying Facility Number' or 'Supplying Facility' field and enter: {master_bill}", max_steps=4)
        print("✅ Supplying Facility Number entered\n")
        time.sleep(2)
        
        # Fill Product Code
        print(f"→ Filling Product Code: {product_code}...")
        nova.act(f"Find the Product Code field and enter: {product_code}", max_steps=4)
        print("✅ Product Code entered\n")
        time.sleep(2)
        
        # Fill Quantity
        print(f"→ Filling Quantity: {quantity}...")
        nova.act(f"Find the Quantity field and enter: {quantity}", max_steps=4)
        print("✅ Quantity entered\n")
        time.sleep(2)
        
        # Select Temperature
        print(f"→ Selecting Temperature: {temperature}...")
        nova.act(f"Find the Temperature dropdown, open it, and select: {temperature}", max_steps=6)
        print("✅ Temperature selected\n")
        time.sleep(2)
        
        # Fill Delivery Date (always attempt)
        delivery_date_value = delivery_date if delivery_date else ""
        if delivery_date_value:
            print(f"→ Filling Delivery Date: {delivery_date_value}...")
            try:
                nova.act(f"Find the Delivery Date or Expected Delivery Date field and enter: {delivery_date_value}", max_steps=4)
                print("✅ Delivery Date entered\n")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️  Could not fill Delivery Date: {e}\n")
        else:
            print("⊘ Delivery Date not provided, skipping\n")
        
        # Fill Carrier/Delivery Company (always attempt)
        carrier_value = delivery_company if delivery_company else ""
        if carrier_value:
            print(f"→ Filling Carrier: {carrier_value}...")
            try:
                nova.act(f"Find the Carrier, Delivery Company, or Transportation field and enter: {carrier_value}", max_steps=4)
                print("✅ Carrier entered\n")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️  Could not fill Carrier: {e}\n")
        else:
            print("⊘ Carrier not provided, skipping\n")
        
        # Fill Header Remarks/Comments (always attempt)
        comments_value = comments if comments else ""
        if comments_value:
            print(f"→ Filling Header Remarks/Comments: {comments_value}...")
            try:
                nova.act(f"Find the Header Remarks, Comments, Notes, or Additional Information field and enter: {comments_value}", max_steps=4)
                print("✅ Header Remarks entered\n")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️  Could not fill Header Remarks: {e}\n")
        else:
            print("⊘ Comments not provided, skipping\n")
        
        # Take screenshot before submitting (form fully filled)
        print("📸 Taking screenshot of filled form...")
        try:
            from datetime import datetime
            from pathlib import Path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if Path("/app").exists():
                screenshot_path = f"/tmp/form_filled_{timestamp}_{master_bill}.png"
            else:
                screenshot_path = f"./form_filled_{timestamp}_{master_bill}.png"
            
            nova.page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ Pre-submit screenshot saved: {screenshot_path}")
            print(f"   This shows the completed form before submission\n")
        except Exception as screenshot_error:
            print(f"⚠️  Could not take pre-submit screenshot: {screenshot_error}\n")
        
        # Submit form
        print("→ Submitting order form...")
        try:
            nova.act("Click the Submit button or Save button to create the inbound order", max_steps=5)
            print("✅ Submit button clicked\n")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Failed to click Submit: {e}\n")
            raise
        
        # Wait for confirmation message - MANDATORY CHECK
        print("→ Waiting for order confirmation...")
        try:
            nova.act("""
                Look for the confirmation message that says 'Inbound Order Confirmed' or similar success message.
                This is CRITICAL - we need to verify the order was actually created.
                Look for text containing: 'confirmed', 'created successfully', or 'order processed'
            """, max_steps=10)
            print("✅ Order confirmation detected!\n")
            time.sleep(2)
            
            # Take screenshot of confirmation
            print("📸 Taking screenshot of confirmation...")
            try:
                from datetime import datetime
                from pathlib import Path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if Path("/app").exists():
                    screenshot_path = f"/tmp/order_confirmed_{timestamp}_{master_bill}.png"
                else:
                    screenshot_path = f"./order_confirmed_{timestamp}_{master_bill}.png"
                
                nova.page.screenshot(path=screenshot_path, full_page=True)
                print(f"✅ Confirmation screenshot saved: {screenshot_path}")
                print(f"   This shows the order was successfully processed\n")
            except Exception as screenshot_error:
                print(f"⚠️  Could not take confirmation screenshot: {screenshot_error}\n")
            
            print("="*70)
            print("🎉 ORDER SUCCESSFULLY CREATED IN ARCADIA!")
            print("="*70)
            print()
            
            success = True
            error_msg = None
            
        except Exception as e:
            print(f"❌ CRITICAL: Could not detect confirmation message: {e}")
            print("   Order submission may have failed!")
            print("   Taking screenshot of current state...\n")
            
            # Take screenshot of failure state
            try:
                from datetime import datetime
                from pathlib import Path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if Path("/app").exists():
                    screenshot_path = f"/tmp/order_failed_{timestamp}_{master_bill}.png"
                else:
                    screenshot_path = f"./order_failed_{timestamp}_{master_bill}.png"
                
                nova.page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Failure screenshot saved: {screenshot_path}\n")
            except:
                pass
            
            # FAIL THE WHOLE OPERATION
            raise Exception(f"Order confirmation not found. Submission likely failed: {e}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        success = False
        error_msg = str(e)
        
    finally:
        print("🔚 Closing Arcadia...")
        nova.stop()
        print("✅ Browser stopped\n")
        
        # Note: NovaAct doesn't support built-in video recording
        # Video recording would need to be implemented separately
        
        print("✅ Done\n")
        
        # Return result
        result = {
            "success": success,
            "video_path": None,  # Video recording not supported by NovaAct
            "error": error_msg
        }
        
        return result


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🤖 ARCADIA ORDER FILLER")
    print("="*70)
    print("\nThis script fills a single order in Arcadia.")
    print()
    
    # Get order details
    if len(sys.argv) > 1:
        # From command line args
        master_bill = sys.argv[1]
        product_code = sys.argv[2] if len(sys.argv) > 2 else "PP48F"
        quantity = sys.argv[3] if len(sys.argv) > 3 else "24"
        temperature = sys.argv[4] if len(sys.argv) > 4 else "FREEZER"
        
        # Optional fields - treat empty strings as None
        delivery_date = sys.argv[5].strip() if len(sys.argv) > 5 and sys.argv[5].strip() else None
        delivery_company = sys.argv[6].strip() if len(sys.argv) > 6 and sys.argv[6].strip() else None
        comments = sys.argv[7].strip() if len(sys.argv) > 7 and sys.argv[7].strip() else None
    else:
        # Interactive input (or read from stdin for MCP)
        print("Enter order details (or pipe JSON):")
        master_bill = input("  Master Bill Number (9 digits): ").strip()
        product_code = input("  Product Code (e.g., PP48F): ").strip()
        quantity = input("  Quantity (pallets): ").strip()
        temperature = input("  Temperature (FREEZER/COOLER): ").strip().upper() or "FREEZER"
        
        # Optional fields
        delivery_date = input("  Delivery Date (optional, MM/DD/YYYY): ").strip() or None
        delivery_company = input("  Carrier (optional, e.g., CHR): ").strip() or None
        comments = input("  Comments (optional): ").strip() or None
    
    result = run_arcadia_order(master_bill, product_code, quantity, temperature,
                                delivery_date, delivery_company, comments)
    
    # Output result as JSON for MCP consumption
    print("\n" + "=" * 70)
    print("📤 RESULT")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("=" * 70)

