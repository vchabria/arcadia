# VNC Setup for Remote Browser Viewing

## Overview
This setup allows you to remotely view the Chromium browser during NovaAct automation on Render.

## Files Added
- `start_vnc.sh` - VNC server startup script
- `start_with_vnc.sh` - Conditional VNC + MCP server entrypoint

## Render Configuration

### 1. Environment Variables

Add these to your Render service:

```bash
# Required
NOVA_ACT_API_KEY=your_nova_act_key
MCP_SECRET=your_mcp_secret

# VNC Control (set to enable)
ENABLE_VNC=true

# Display (automatically set)
DISPLAY=:99
```

### 2. Port Configuration

**Exposed Ports:**
- `10000` - MCP HTTP server (primary)
- `5900` - VNC server (direct VNC client)
- `6080` - noVNC web interface (browser-based)

**Render Settings:**
- Set **Port** to `10000` in Render dashboard
- For VNC access, you may need to upgrade to a plan that supports additional ports

### 3. Persistent Disk

**Critical**: Mount persistent disk at `/app/contexts`

In Render:
1. Go to your service → **Disks**
2. Create disk: **Name:** `contexts`, **Mount Path:** `/app/contexts`
3. This preserves browser sessions between deployments

### 4. Build Command

```bash
# Render auto-detects Dockerfile
# No custom build command needed
```

### 5. Start Command

Already configured in Dockerfile:
```bash
./start_with_vnc.sh
```

## Accessing VNC

### Option 1: noVNC (Browser-Based) - Easiest
```
http://your-render-app.onrender.com:6080/vnc.html
```

### Option 2: Direct VNC Client
```
vnc://your-render-app.onrender.com:5900
```
Use any VNC client (RealVNC, TigerVNC, etc.)

## Testing Locally

### With VNC enabled:
```bash
docker build -t arcadia-mcp .
docker run -p 10000:10000 -p 6080:6080 -p 5900:5900 \
  -e ENABLE_VNC=true \
  -e NOVA_ACT_API_KEY=your_key \
  -e MCP_SECRET=test123 \
  arcadia-mcp
```

Then open: `http://localhost:6080/vnc.html`

### Without VNC (production default):
```bash
docker run -p 10000:10000 \
  -e NOVA_ACT_API_KEY=your_key \
  -e MCP_SECRET=test123 \
  arcadia-mcp
```

## Important Notes

✅ **VNC is optional** - Set `ENABLE_VNC=false` (or omit) in production for better performance
✅ **No password** - VNC runs with `-nopw` for convenience (consider adding auth for production)
✅ **Browser must be non-headless** - Already configured in `run_arcadia_only.py`
✅ **Persistent disk required** - Browser sessions save to `/app/contexts/arcadia_profile`

## Troubleshooting

**Browser not visible in VNC:**
- Check `ENABLE_VNC=true` is set
- Verify browser is running with `headless=False`
- Check logs: `docker logs <container_id>`

**VNC connection refused:**
- Ensure ports 5900 and 6080 are exposed in Render
- May require Render paid plan for custom ports

**Black screen in noVNC:**
- Wait 5-10 seconds for Xvfb to initialize
- Check display is set: `echo $DISPLAY` should show `:99`

## Production Recommendations

For production (no VNC needed):
```bash
# Remove or set to false
ENABLE_VNC=false
```

This saves resources and improves performance.

