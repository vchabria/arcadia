# Render Deployment Guide

## 🚀 Deploy Inbound MCP Server to Render

This guide covers deploying the Arcadia Inbound Order MCP Server to Render as a persistent production service.

---

## Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at https://render.com
3. **Nova Act API Key** - Your browser automation API key
4. **MCP Secret** - Generate a secure random string for API authentication

---

## Environment Variables Required

Set these in Render's Environment section:

```bash
# REQUIRED: Nova Act API Key for browser automation
NOVA_ACT_API_KEY=your_nova_act_key_here

# REQUIRED: MCP authentication secret
MCP_SECRET=your_secure_random_secret_here
```

---

## Deployment Steps

### 1. Push Code to GitHub

```bash
cd /path/to/inbound_mcp
git init
git add .
git commit -m "Initial commit - Arcadia MCP Server"
git remote add origin https://github.com/yourusername/arcadia-mcp-server.git
git push -u origin main
```

### 2. Create New Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository containing `inbound_mcp`

### 3. Configure Service

**Basic Settings:**
- **Name:** `arcadia-mcp-server` (or your preferred name)
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** Leave empty (or specify `inbound_mcp` if repo contains multiple projects)
- **Runtime:** `Docker`
- **Instance Type:** `Starter` (or higher for production)

**Build Settings:**
- **Dockerfile Path:** `Dockerfile` (already configured)
- Render will automatically detect the Dockerfile

**Environment Variables:**
Click **"Add Environment Variable"** and add:

```
NOVA_ACT_API_KEY = <your_nova_act_api_key>
MCP_SECRET = <your_secure_mcp_secret>
```

**Auto-Deploy:**
- Enable **"Auto-Deploy"** for automatic deployments on git push

### 4. Deploy

Click **"Create Web Service"**

Render will:
1. Clone your repository
2. Build the Docker image
3. Install dependencies
4. Start the service on port 10000
5. Provide you with a public URL

---

## Service URLs

After deployment, you'll get a URL like:
```
https://arcadia-mcp-server.onrender.com
```

### Test Your Deployment

**Health Check:**
```bash
curl https://your-app.onrender.com/health
```

**List MCP Tools:**
```bash
curl https://your-app.onrender.com/tools
```

**Call MCP Tool (with authentication):**
```bash
curl -X POST https://your-app.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -H "x-mcp-key: your_mcp_secret_here" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_arcadia_order",
      "arguments": {
        "master_bill_number": "123456789",
        "product_code": "PP48F",
        "quantity": 24,
        "temperature": "FREEZER",
        "delivery_date": "12/24/2025",
        "delivery_company": "CHR",
        "comments": "Test order"
      }
    },
    "id": 1
  }'
```

---

## MCP Authentication

All requests (except `/health`) require authentication via the `x-mcp-key` header:

```bash
x-mcp-key: your_mcp_secret_value
```

**Without valid key:**
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing x-mcp-key header"
}
```

---

## Available MCP Tools

1. **`extract_inbound_orders`** - Extract orders from Gmail
2. **`add_to_arcadia`** - Submit extracted orders to Arcadia
3. **`create_arcadia_order`** - Create a single order with all fields
4. **`run_full_pipeline`** - Complete automation (Gmail → Arcadia)

---

## Monitoring & Logs

### View Logs
- Go to your service dashboard on Render
- Click **"Logs"** tab
- Real-time logs show all requests and operations

### Health Monitoring
Render automatically monitors `/health` endpoint
- Service will auto-restart if health checks fail
- Configure alerts in Render dashboard

### Metrics
- View request rates, response times, and errors
- Available in Render dashboard under **"Metrics"**

---

## Troubleshooting

### Service Won't Start
- Check **Logs** for build errors
- Verify all environment variables are set
- Ensure Dockerfile is in repository root

### Authentication Fails
- Verify `MCP_SECRET` is set in Render environment
- Check that `x-mcp-key` header matches the secret
- Case-sensitive comparison

### Browser Automation Fails
- Verify `NOVA_ACT_API_KEY` is valid
- Check Nova Act account has sufficient credits
- View logs for detailed error messages

### Timeout Issues
- Render free tier has 15-minute request timeout
- Upgrade to paid plan for longer operations
- Consider async operations for long-running tasks

---

## Updating the Service

### Automatic Deployment
Push to GitHub main branch:
```bash
git add .
git commit -m "Update MCP server"
git push origin main
```

Render auto-deploys within seconds.

### Manual Deployment
In Render dashboard:
1. Go to your service
2. Click **"Manual Deploy"**
3. Select branch and deploy

---

## Cost Optimization

### Free Tier
- Service sleeps after 15 min of inactivity
- First request wakes it up (~30s delay)
- 750 hours/month free

### Paid Plans ($7+/month)
- Always-on service (no sleep)
- Better performance
- Longer request timeouts
- Custom domains

---

## Security Best Practices

1. **Never commit secrets** - Use environment variables only
2. **Rotate MCP_SECRET** regularly
3. **Monitor logs** for suspicious activity
4. **Use HTTPS** - Always use the Render HTTPS URL
5. **Restrict access** - Consider IP allowlisting if possible

---

## Integration with Omni

Configure Omni to use your Render URL:

**MCP Server URL:**
```
https://your-app.onrender.com
```

**Authentication Header:**
```
x-mcp-key: your_mcp_secret
```

**Tools Available:**
- All 4 MCP tools are automatically discovered
- Omni will show them in the tools panel
- Use for Gmail extraction and Arcadia order creation

---

## Support

**Issues:**
- Check Render logs first
- Review this deployment guide
- Verify environment variables
- Test endpoints with curl

**Resources:**
- Render Docs: https://render.com/docs
- MCP Specification: https://modelcontextprotocol.io
- NovaAct Docs: https://nova-act.com/docs

---

## Production Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Environment variables set
- [ ] Service deployed successfully
- [ ] Health check returns 200 OK
- [ ] MCP authentication working
- [ ] Test order creation works
- [ ] Logs show successful operations
- [ ] Monitoring configured
- [ ] Backup MCP_SECRET stored securely

---

**Status:** ✅ Production Ready

Your MCP server is now deployed and accessible 24/7 from anywhere!

