# 📸 Screenshot URLs - Quick Reference Card

Save this for easy access when you need screenshots for emails!

---

## 🔗 Your Service URLs

Replace `YOUR-SERVICE-NAME` with your actual Render service name (probably `inbound-mcp`)

---

## 📋 LIST ALL SCREENSHOTS

```
https://YOUR-SERVICE-NAME.onrender.com/screenshots
```

**Returns:** JSON with all available screenshots organized by type

**Use for:** Checking what screenshots exist, getting exact filenames

---

## ⚡ QUICK DOWNLOAD LINKS

### Latest Login Screenshot
```
https://YOUR-SERVICE-NAME.onrender.com/screenshots/latest/login
```
**Use for:** ✅ Login verification emails

---

### Latest Form Screenshot  
```
https://YOUR-SERVICE-NAME.onrender.com/screenshots/latest/form
```
**Use for:** 📦 Order completion proof emails

---

### Latest Any Screenshot
```
https://YOUR-SERVICE-NAME.onrender.com/screenshots/latest/download
```
**Use for:** Most recent activity of any type

---

## 🎯 SPECIFIC SCREENSHOT

```
https://YOUR-SERVICE-NAME.onrender.com/screenshots/FILENAME.png
```

**Example filenames:**
- `login_success_20251228_153045.png`
- `login_failed_20251228_120130.png`
- `form_filled_20251228_153045_001904712.png`

**Use for:** Getting a specific screenshot when you know the exact filename

---

## 📧 FOR EMAIL ATTACHMENTS

### Method 1: Direct Browser Download
1. Open URL in browser
2. Right-click → "Save Image As..."
3. Attach to email

### Method 2: Copy Image
1. Open URL in browser
2. Right-click → "Copy Image"
3. Paste directly into email

### Method 3: Embed Link
Just paste the URL in your email - they can click to view

---

## 🔍 SCREENSHOT TYPES

| Type | Filename Pattern | When Created | What It Shows |
|------|-----------------|--------------|---------------|
| ✅ Login Success | `login_success_YYYYMMDD_HHMMSS.png` | After successful login | Arcadia dashboard |
| ❌ Login Failed | `login_failed_YYYYMMDD_HHMMSS.png` | When login fails | Error page/login form |
| 📝 Form Filled | `form_filled_YYYYMMDD_HHMMSS_BILL.png` | Before form submission | Completed order form |

---

## 💾 SAVE THIS AS BOOKMARKS

1. Go to your browser bookmarks
2. Create folder: "Arcadia Screenshots"
3. Add these bookmarks:

**List All:**
```
Name: Arcadia - All Screenshots
URL: https://YOUR-SERVICE-NAME.onrender.com/screenshots
```

**Latest Login:**
```
Name: Arcadia - Latest Login
URL: https://YOUR-SERVICE-NAME.onrender.com/screenshots/latest/login
```

**Latest Order:**
```
Name: Arcadia - Latest Order Form
URL: https://YOUR-SERVICE-NAME.onrender.com/screenshots/latest/form
```

---

## 📱 MOBILE-FRIENDLY

All URLs work on mobile devices too! Save to your phone's home screen for quick access.

---

## ⚠️ TROUBLESHOOTING

### "Screenshot not found"
- Means no activity has occurred yet
- Trigger a test order to generate screenshots

### "Service not responding"
- Check if service is running in Render dashboard
- Verify latest code was deployed

### "Wrong screenshot showing"
- Use `/screenshots` endpoint to list all available
- Download specific one by filename

---

## 🎯 MOST COMMON USE CASE

**For login verification emails:**

1. Open: `https://YOUR-SERVICE-NAME.onrender.com/screenshots/latest/login`
2. Right-click → Save Image As... → `arcadia_login_proof.png`
3. Attach to email
4. Send! ✉️

---

**Print this page and keep it handy! 📄**

