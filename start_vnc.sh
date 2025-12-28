#!/bin/bash
set -e

export DISPLAY=:99

# Virtual display
Xvfb :99 -screen 0 1280x800x16 &

# Window manager
fluxbox &

# VNC server
x11vnc -display :99 -nopw -forever -shared &

# noVNC (browser-based)
websockify --web=/usr/share/novnc/ 6080 localhost:5900

