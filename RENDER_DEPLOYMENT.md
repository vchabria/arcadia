# Render Deployment Guide

## ✅ Setup is Ready

Dockerfile CMD: `/app/start_with_vnc.sh` ✅  
Conditional VNC: Checks `ENABLE_VNC=true` ✅

## Steps

### 1. Environment Variables (Render Dashboard)
```
NOVA_ACT_API_KEY=your_key
MCP_SECRET=your_secret
ENABLE_VNC=true
```

### 2. Persistent Disk
Name: `contexts`  
Mount: `/app/contexts`

### 3. Deploy & Watch Logs

You MUST see:
```
🖥️  VNC enabled - Starting VNC server...
✅ VNC listening on :6080
🚀 Starting MCP server on port 10000...
```

### 4. Access VNC
`https://your-app.onrender.com:6080/vnc.html`

⚠️ Port 6080 requires Render paid plan

## Troubleshooting

- No "Starting VNC"? → Check `ENABLE_VNC=true` 
- Can't connect? → Port 6080 not public (Render limitation)
- Session lost? → Verify disk at `/app/contexts`
