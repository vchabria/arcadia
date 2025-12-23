# Browser Profile Setup for Omni

## 📦 What to Upload to Omni

Upload these browser profile archives to Omni:

1. **`arcadia_profile.tar.gz`** (54 MB) - Contains saved Arcadia login session
2. **`gmail_profile.tar.gz`** (~31 MB) - Contains saved Gmail login session

## 📍 Where Omni Should Extract Them

Extract the profiles to:
```
/workspace/contexts/
├── arcadia_profile/     ← Extract arcadia_profile.tar.gz here
└── gmail_profile/       ← Extract gmail_profile.tar.gz here
```

## 🔧 What to Tell Omni

**Tell Omni:**

```
Browser Profile Location: /workspace/contexts/arcadia_profile

This directory contains cached browser authentication data:
- Cookies (saved login cookies)
- Login Data (saved passwords)  
- Preferences (browser settings)
- Default/ directory (Chrome profile)

The SDK will use this profile to automatically log in to Arcadia.
No OAuth tokens needed - authentication is handled via saved browser cookies.

Extract arcadia_profile.tar.gz to /workspace/contexts/arcadia_profile/
Extract gmail_profile.tar.gz to /workspace/contexts/gmail_profile/
```

## ✅ Verification

After extraction, verify:
```bash
ls -la /workspace/contexts/arcadia_profile/Default/Cookies
# Should show: Cookies file exists ✅
```

## 🚀 SDK Usage

Once profiles are in `/workspace/contexts/`, the SDK will automatically find them because:
- Scripts run from `/workspace/stagehand-test/` directory
- Scripts use relative path: `./contexts/arcadia_profile`
- This resolves to: `/workspace/stagehand-test/contexts/arcadia_profile`

**Important:** Make sure the directory structure is:
```
/workspace/
├── contexts/              ← Browser profiles here
│   ├── arcadia_profile/
│   └── gmail_profile/
└── stagehand-test/        ← Scripts run from here
    └── (scripts use ./contexts/arcadia_profile)
```

