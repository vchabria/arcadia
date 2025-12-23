# 🚀 Deployment Guide

Complete guide for deploying the Inbound Order MCP Server to production.

---

## 🎯 Deployment Options

1. **ngrok** - Quick local development (recommended for testing)
2. **Render** - Easy cloud deployment with free tier
3. **Railway** - Modern platform with generous free tier
4. **Docker + VPS** - Full control (DigitalOcean, AWS, etc.)

---

## 🌐 Option 1: ngrok (Fastest for Testing)

### Prerequisites
- Server running locally
- ngrok installed

### Steps

1. **Start the MCP server:**
```bash
cd inbound_mcp
./run_server.sh
```

2. **In another terminal, start ngrok:**
```bash
ngrok http 8080
```

3. **Copy the HTTPS URL:**
```
Forwarding: https://abc123.ngrok.io -> http://localhost:8080
```

4. **Use in Omni:**
```
MCP Endpoint: https://abc123.ngrok.io/mcp
```

### Pros & Cons
✅ Instant setup  
✅ HTTPS included  
✅ Great for testing  
❌ Requires local machine running  
❌ URL changes on restart (unless paid plan)

---

## ☁️ Option 2: Render (Free Cloud)

### Prerequisites
- GitHub account
- Render account (free)

### Steps

1. **Push code to GitHub:**
```bash
cd inbound_mcp
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/inbound-mcp.git
git push -u origin main
```

2. **Create Web Service on Render:**
- Go to https://render.com
- Click "New +" → "Web Service"
- Connect your GitHub repo
- Configure:
  - **Name**: inbound-mcp
  - **Environment**: Docker
  - **Plan**: Free
  - **Port**: 8080

3. **Add environment variables** (if needed)

4. **Deploy!**
- Render will build and deploy automatically
- Your URL: `https://inbound-mcp.onrender.com`

5. **Use in Omni:**
```
MCP Endpoint: https://inbound-mcp.onrender.com/mcp
```

### Pros & Cons
✅ Free tier available  
✅ HTTPS included  
✅ Auto-deployment from Git  
✅ Persistent URL  
❌ Free tier spins down after 15 min inactivity  
❌ Cold start delay (~30 seconds)

---

## 🚂 Option 3: Railway (Modern Platform)

### Prerequisites
- GitHub account
- Railway account (free)

### Steps

1. **Push code to GitHub** (same as Render)

2. **Deploy on Railway:**
- Go to https://railway.app
- Click "New Project" → "Deploy from GitHub repo"
- Select your repo
- Railway auto-detects Dockerfile

3. **Configure:**
- Port: 8080 (auto-detected)
- Add environment variables if needed

4. **Get URL:**
- Railway provides: `https://yourapp.up.railway.app`

5. **Use in Omni:**
```
MCP Endpoint: https://yourapp.up.railway.app/mcp
```

### Pros & Cons
✅ $5 free credit monthly  
✅ No cold starts  
✅ Fast deployments  
✅ Great developer experience  
❌ Requires credit card for free tier  

---

## 🐳 Option 4: Docker + VPS (Full Control)

### Prerequisites
- VPS (DigitalOcean, AWS EC2, Linode, etc.)
- Docker installed on VPS

### Steps

1. **SSH into your VPS:**
```bash
ssh user@your-server-ip
```

2. **Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

3. **Clone your repo:**
```bash
git clone https://github.com/yourusername/inbound-mcp.git
cd inbound-mcp
```

4. **Build and run:**
```bash
docker-compose up -d
```

5. **Set up reverse proxy (nginx):**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

6. **Get SSL certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

7. **Use in Omni:**
```
MCP Endpoint: https://your-domain.com/mcp
```

### Pros & Cons
✅ Full control  
✅ No cold starts  
✅ Custom domain  
✅ Can scale  
❌ Requires server management  
❌ Monthly cost ($5-10+)

---

## 🔒 Production Checklist

Before going live, ensure:

### Security
- [ ] Environment variables set (not hardcoded)
- [ ] HTTPS enabled (SSL certificate)
- [ ] CORS properly configured
- [ ] Rate limiting added (if needed)
- [ ] Authentication considered (if exposing publicly)

### Reliability
- [ ] Health check endpoint working
- [ ] Error handling tested
- [ ] Logging configured
- [ ] Browser profiles persist across restarts
- [ ] Backup strategy for profiles

### Performance
- [ ] Server has adequate resources (2GB+ RAM recommended)
- [ ] Browser automation runs in headless mode (set in handlers.py)
- [ ] Timeout values configured appropriately

### Monitoring
- [ ] Health checks automated
- [ ] Error notifications set up
- [ ] Usage logs reviewed regularly

---

## 🧪 Testing Deployment

After deployment, test all endpoints:

```bash
# Replace URL with your deployment URL
DEPLOYMENT_URL="https://your-deployment.com"

# Test health
curl $DEPLOYMENT_URL/health

# Test tools list
curl $DEPLOYMENT_URL/tools

# Test MCP initialize
curl -X POST $DEPLOYMENT_URL/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":0}'
```

---

## 🔄 Continuous Deployment

### GitHub Actions (Example)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Trigger Render Deploy
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

---

## 📊 Monitoring

### Health Check Monitoring

Use a service like UptimeRobot or Better Uptime:
- URL: `https://your-deployment.com/health`
- Check interval: 5 minutes
- Alert when down

### Log Monitoring

View logs:
```bash
# Docker
docker logs inbound-mcp-server -f

# Railway
railway logs

# Render
Check dashboard → Logs tab
```

---

## 🆘 Troubleshooting

### Issue: Server not responding

**Check:**
- Health endpoint: `curl https://your-url.com/health`
- Server logs for errors
- Port 8080 is exposed
- Firewall rules allow traffic

### Issue: Browser automation failing

**Check:**
- Browser profiles are persistent
- Adequate memory (2GB+ RAM)
- Chrome/Chromium installed
- NovaAct dependencies installed

### Issue: Cold start timeout (Render)

**Solutions:**
- Upgrade to paid plan (no cold starts)
- Use a cron job to ping server every 10 minutes
- Accept 30-second initial delay

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid | Best For |
|----------|-----------|------|----------|
| ngrok | Yes* | $8/mo | Local testing |
| Render | Yes | $7/mo | Hobby projects |
| Railway | $5 credit | Pay as you go | Production |
| DigitalOcean | No | $6/mo | Full control |

*ngrok free tier has random URLs

---

## 🎯 Recommended Approach

**For Testing:**
1. Start with ngrok for immediate testing
2. Keep server running locally

**For Production:**
1. Use Railway or Render for easy deployment
2. Set up monitoring
3. Configure custom domain (optional)
4. Add authentication if exposing publicly

---

**Your MCP server is ready for production! 🚀**
