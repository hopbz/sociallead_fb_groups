#!/bin/sh
set -eu

export DISPLAY="${DISPLAY:-:99}"
VNC_RESOLUTION="${VNC_RESOLUTION:-1365x850x24}"
DISPLAY_NUMBER="${DISPLAY#:}"
DISPLAY_NUMBER="${DISPLAY_NUMBER%%.*}"

# Docker restarts preserve /tmp inside the container, while Xvfb leaves these
# files behind after a forced stop.
rm -f "/tmp/.X${DISPLAY_NUMBER}-lock" "/tmp/.X11-unix/X${DISPLAY_NUMBER}"
mkdir -p /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix

Xvfb "$DISPLAY" -screen 0 "$VNC_RESOLUTION" -ac +extension RANDR >/tmp/xvfb.log 2>&1 &
XVFB_PID=$!
sleep 1
fluxbox >/tmp/fluxbox.log 2>&1 &
FLUXBOX_PID=$!
x11vnc -display "$DISPLAY" -rfbport 5900 -localhost -forever -shared -nopw >/tmp/x11vnc.log 2>&1 &
X11VNC_PID=$!
websockify --web=/usr/share/novnc 6080 localhost:5900 >/tmp/novnc.log 2>&1 &
NOVNC_PID=$!
sleep 1

for PID in "$XVFB_PID" "$FLUXBOX_PID" "$X11VNC_PID" "$NOVNC_PID"; do
    if ! kill -0 "$PID" 2>/dev/null; then
        cat /tmp/xvfb.log /tmp/fluxbox.log /tmp/x11vnc.log /tmp/novnc.log >&2
        exit 1
    fi
done

exec uvicorn app.main:app --host 0.0.0.0 --port 3001
