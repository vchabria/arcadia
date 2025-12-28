# 📸 Login Screenshots Guide

## Overview

After the Arcadia login automation successfully authenticates using the secret keys stored in Render, the system automatically captures a screenshot of the logged-in dashboard.

---

## 🎯 What Gets Captured

- **Full page screenshot** of the Arcadia dashboard after successful login
- **Timestamp** included in filename for easy identification
- **Proof of authentication** showing the system successfully logged in

---

## 📂 Where Screenshots Are Saved

### On Render (Production)

Screenshots are saved to: `/tmp/login_success_YYYYMMDD_HHMMSS.png`

Example: `/tmp/login_success_20251228_153045.png`

### Locally (Development)

Screenshots are saved to: `./login_success_YYYYMMDD_HHMMSS.png`

Example: `./login_success_20251228_153045.png`

---

## 🔍 How to Access Screenshots on Render

### Method 1: Using Render Shell (Recommended)

1. Go to your Render Dashboard
2. Navigate to your `inbound-mcp` service
3. Click on the **"Shell"** tab
4. Run the following commands:

```bash
# List all login screenshots
ls -lh /tmp/login_success_*.png

# View the most recent screenshot
ls -t /tmp/login_success_*.png | head -1

# Copy screenshot to a downloadable location (if needed)
# Note: Render shell doesn't support direct downloads, but you can view the file path
```

### Method 2: Download via Service Logs

The screenshot path is logged in the service output. Look for:

```
📸 Screenshot saved: /tmp/login_success_20251228_153045.png
   This screenshot shows the successful login to Arcadia dashboard
```

### Method 3: Add an API Endpoint (Advanced)

You can add an endpoint to serve the screenshots. Here's how:

1. Add this to your `mcp/server.py`:

```python
from fastapi.responses import FileResponse
from pathlib import Path
import glob

@app.get("/screenshots")
async def list_screenshots():
    """List all available login screenshots"""
    screenshots = glob.glob("/tmp/login_success_*.png")
    screenshots.sort(reverse=True)  # Most recent first
    return {
        "screenshots": [Path(s).name for s in screenshots],
        "count": len(screenshots)
    }

@app.get("/screenshots/{filename}")
async def get_screenshot(filename: str):
    """Download a specific screenshot"""
    file_path = f"/tmp/{filename}"
    if Path(file_path).exists():
        return FileResponse(file_path, media_type="image/png")
    return {"error": "Screenshot not found"}
```

2. Then access via:
   - List: `https://your-service.onrender.com/screenshots`
   - Download: `https://your-service.onrender.com/screenshots/login_success_20251228_153045.png`

---

## 🚀 When Are Screenshots Taken?

Screenshots are automatically captured when:

1. ✅ **First login after deployment** - When credentials from Render Secret Files are used
2. ✅ **Session expires** - When auto-login triggers again
3. ✅ **Profile is cleared** - When the browser profile is reset

**Note:** If already logged in (session persists), no new screenshot is taken.

---

## 📧 Using Screenshots for Email Updates

### Example Email Template

**Subject:** Arcadia Login Automation - Successfully Configured ✅

**Body:**
```
Hi Team,

The Arcadia inbound order automation has been successfully configured with secure credentials on Render.

✅ Login Status: Successful
🔑 Authentication: Using Render Secret Files
📸 Screenshot: [Attach login_success screenshot]
🕐 Timestamp: [Date/Time from filename]

The system is now ready to process inbound orders automatically via the Omni agent.

Best regards,
[Your name]
```

---

## 🔒 Security Notes

1. **Screenshots contain dashboard data** - Only share with authorized personnel
2. **/tmp directory** - Files may be cleared on service restart (ephemeral)
3. **Credentials not visible** - Login form is not captured, only the post-login dashboard
4. **No passwords in logs** - Passwords are masked as `********` in logs

---

## 🛠️ Troubleshooting

### Screenshot Not Found

If screenshots aren't being generated:

1. Check service logs for screenshot errors:
```
⚠️  Could not take screenshot: [error message]
```

2. Verify the login actually succeeded:
```
✅ Login successful! Session saved to profile.
```

3. Check if /tmp is writable (should be by default on Render)

### Download Not Working

1. Verify the file exists via Shell
2. Check filename spelling (case-sensitive)
3. Ensure timestamp format matches: `YYYYMMDD_HHMMSS`

---

## 📋 Quick Reference

| Action | Command/URL |
|--------|-------------|
| List screenshots in Shell | `ls -lh /tmp/login_success_*.png` |
| Find most recent | `ls -t /tmp/login_success_*.png \| head -1` |
| Check file size | `du -h /tmp/login_success_*.png` |
| View via endpoint | `GET /screenshots` |
| Download specific | `GET /screenshots/{filename}` |

---

## 💡 Tips

1. **First deployment**: Trigger a test order to force a login and capture screenshot
2. **Regular checks**: Screenshots prove the system is maintaining authentication
3. **Email proof**: Attach screenshots when reporting successful configuration to stakeholders
4. **Debugging**: Screenshots help diagnose if the correct page loaded after login

---

## 🎬 Next Steps

1. Deploy the updated code to Render
2. Set up Arcadia credentials in Render Secret Files
3. Trigger a test order (this will force login if needed)
4. Access Shell to verify screenshot was saved
5. Download screenshot for your email updates

---

**Questions?** Check the main README.md or contact your dev team.

