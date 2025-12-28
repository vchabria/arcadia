# 📧 Quick Email Guide - Login & Order Screenshots

## 🎯 What Screenshots Are Available

The system automatically captures screenshots at key moments:

1. **✅ Login Success** - Dashboard after successful authentication
2. **❌ Login Failed** - Page state when login fails (for debugging)
3. **📝 Form Filled** - Completed order form right before submission

---

## 🔗 Easy Access URLs

Once deployed, use these URLs (replace `your-service-name` with your actual Render service name):

### List All Screenshots
```
https://your-service-name.onrender.com/screenshots
```

**Example Response:**
```json
{
  "success": true,
  "screenshots": [
    "form_filled_20251228_153045_001904712.png",
    "login_success_20251228_153030.png",
    "login_failed_20251228_120130.png"
  ],
  "count": 3,
  "by_type": {
    "login_success": ["login_success_20251228_153030.png"],
    "login_failed": ["login_failed_20251228_120130.png"],
    "forms_filled": ["form_filled_20251228_153045_001904712.png"]
  },
  "directory": "/tmp",
  "note": "Screenshots show login attempts and completed order forms before submission"
}
```

### Download Latest Screenshots (Easiest!)

**Any screenshot (most recent):**
```
https://your-service-name.onrender.com/screenshots/latest/download
```

**Latest login screenshot:**
```
https://your-service-name.onrender.com/screenshots/latest/login
```
👆 **Use this for email proof of login!**

**Latest order form screenshot:**
```
https://your-service-name.onrender.com/screenshots/latest/form
```
👆 **Use this to show completed orders!**

### Download Specific Screenshot
```
https://your-service-name.onrender.com/screenshots/login_success_20251228_153045.png
https://your-service-name.onrender.com/screenshots/form_filled_20251228_153045_001904712.png
```

---

## 📝 Steps to Get Screenshot for Email

1. **Deploy the code** to Render (push to GitHub)
2. **Ensure credentials are set** in Render Secret Files:
   - File: `arcadia_credentials.env`
   - Content:
     ```
     ARCADIA_USERNAME=your_email@example.com
     ARCADIA_PASSWORD=your_password
     ```
3. **Trigger a test order** to force login (if needed):
   ```bash
   curl -X POST https://your-service-name.onrender.com/mcp \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_mcp_secret" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "create_arcadia_order",
         "arguments": {
           "master_bill_number": "TEST123",
           "product_code": "FPP20V2F",
           "quantity": 1,
           "temperature": "FREEZER",
           "delivery_date": "12/31/2025",
           "comments": "Test order to verify login"
         }
       },
       "id": 1
     }'
   ```
4. **Download the screenshots**:
   - **Login proof**: `https://your-service-name.onrender.com/screenshots/latest/login`
   - **Order form proof**: `https://your-service-name.onrender.com/screenshots/latest/form`
   - Right-click → Save Image As...
5. **Attach to email** and send!

---

## 📧 Email Templates

### Template 1: Initial Setup - Login Verification

**Subject:** ✅ Arcadia Automation Setup Complete - Login Verified

**Body:**

```
Hi [Name],

Great news! The Arcadia inbound order automation is now fully operational on Render.

✅ Status: Deployed and Running
🔐 Authentication: Successfully configured with secure credentials
🤖 Automation: Ready to process orders via Omni agent

I've attached a screenshot showing the successful login to the Arcadia dashboard. 
This confirms the system is authenticating properly and ready to create orders.

Technical Details:
- Service URL: https://your-service-name.onrender.com
- Authentication: Using Render Secret Files (secure)
- Browser Automation: NovaAct (cloud-based)
- Profile Persistence: Enabled on persistent disk

Next Steps:
The system is now ready to receive order creation requests from the Omni agent. 
Orders from Gmail will be automatically extracted and submitted to Arcadia.

Let me know if you have any questions!

Best,
[Your Name]
```

**Attachments:**
- Download: `https://your-service-name.onrender.com/screenshots/latest/login`

---

### Template 2: Order Completion Proof

**Subject:** 📦 Order Processed Successfully - [Master Bill Number]

**Body:**

```
Hi [Name],

I wanted to confirm that the order has been successfully processed in Arcadia.

📦 Order Details:
- Master Bill: [Master Bill Number]
- Product: [Product Code]
- Quantity: [Quantity]
- Temperature: [Temperature Zone]
- Delivery Date: [Date]

✅ Status: Form completed and submitted to Arcadia
🤖 Processed by: Automated system via Omni agent
📸 Proof: Attached screenshot shows the completed form before submission

The screenshot shows all fields filled correctly before the form was submitted.
The order should now be visible in the Arcadia system.

Please let me know if you need any additional information.

Best,
[Your Name]
```

**Attachments:**
- Download: `https://your-service-name.onrender.com/screenshots/latest/form`

---

### Template 3: Troubleshooting - Login Failed

**Subject:** ⚠️ Arcadia Automation - Login Issue Detected

**Body:**

```
Hi [Name],

The Arcadia automation system detected a login issue that requires attention.

❌ Issue: Login to Arcadia dashboard failed
🕐 Time: [Check timestamp in filename]
📸 Screenshot: Attached showing the state when login failed

Possible Causes:
- Credentials may have changed
- Arcadia website may have updated their login form
- Session may have been invalidated

Next Steps:
1. Verify credentials are still valid
2. Update credentials in Render Secret Files if needed
3. Check Arcadia for any security alerts or required actions

I've attached a screenshot showing the exact state when the login failed,
which should help diagnose the issue.

Please let me know if you'd like me to investigate further.

Best,
[Your Name]
```

**Attachments:**
- Download: `https://your-service-name.onrender.com/screenshots/latest/login`
  (This will be the failed login screenshot if that's the most recent)

---

## 🔍 Troubleshooting

### "No screenshots found"

This means login hasn't happened yet. Trigger it by:

1. Making a test order request (see Step 3 above)
2. Checking Render logs for login activity
3. Verifying credentials are set in Render Secret Files

### "Screenshot endpoint returns 404"

Check:
1. Service is running: `https://your-service-name.onrender.com/health`
2. Deployment succeeded in Render dashboard
3. Latest code was pushed to GitHub

### Need the screenshot RIGHT NOW?

Use Render Shell:

1. Go to Render Dashboard → Your Service → Shell
2. Run: `ls -lh /tmp/*.png` (shows all screenshot types)
3. Note the filename
4. Download via: `https://your-service-name.onrender.com/screenshots/[filename]`

---

## 💡 Pro Tips

1. **Bookmark these URLs** for quick access:
   ```
   Login: https://your-service-name.onrender.com/screenshots/latest/login
   Form: https://your-service-name.onrender.com/screenshots/latest/form
   ```

2. **Check screenshot list** to see all activity:
   ```
   https://your-service-name.onrender.com/screenshots
   ```

3. **Include in status emails** - Download and attach whenever updating stakeholders

4. **Verify timestamp** - The filename shows when action occurred (YYYYMMDD_HHMMSS)

5. **Track orders** - Form screenshots include master bill number in filename

6. **Monitor failures** - Check for `login_failed_*.png` files regularly

---

**Your service name is likely:**
- `inbound-mcp` or
- `omni-inbound-mcp` or
- Whatever you named it in Render

Find it in your Render Dashboard!

