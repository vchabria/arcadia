#!/bin/bash
set -e

export DISPLAY=:99

echo "🔧 Starting virtual display (Xvfb)..."
# Virtual display
Xvfb :99 -screen 0 1280x800x16 &
sleep 1

echo "🪟 Starting window manager (Fluxbox)..."
# Window manager
fluxbox &
sleep 1

echo "🔐 Starting VNC server (x11vnc)..."
# VNC server
x11vnc -display :99 -nopw -forever -shared &
sleep 1

echo "🌐 Starting noVNC web interface..."
# noVNC (browser-based)
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &

echo "✅ VNC listening on :6080"

