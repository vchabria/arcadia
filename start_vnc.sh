#!/bin/bash
set -e

export DISPLAY=:99

echo "🔧 Starting virtual display (Xvfb)..."
Xvfb :99 -screen 0 1280x800x16 &
sleep 1

echo "🪟 Starting window manager (Fluxbox)..."
fluxbox &
sleep 1

echo "🔐 Starting VNC server (x11vnc)..."
x11vnc -display :99 -nopw -forever -shared &
sleep 1

echo "🌐 Starting noVNC web interface on 0.0.0.0:6080..."
# Run websockify as standalone service (NOT through FastAPI)
websockify --web=/usr/share/novnc 0.0.0.0:6080 localhost:5900

