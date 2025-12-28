# Production Dockerfile for Render Deployment
# Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright + VNC
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Create directories for browser profiles (if needed)
RUN mkdir -p /app/contexts

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=10000
ENV DISPLAY=:99
ENV VNC_PORT=5900
ENV NOVNC_PORT=6080

# Expose ports (MCP server + VNC)
EXPOSE 10000 5900 6080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:10000/health')"

# Copy startup scripts
COPY start_with_vnc.sh /app/start_with_vnc.sh
COPY start_vnc.sh /app/start_vnc.sh
RUN chmod +x /app/start_with_vnc.sh /app/start_vnc.sh

# Run the application with VNC
CMD ["/app/start_with_vnc.sh"]
