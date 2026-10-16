#!/bin/bash
# Opens JPF Dashboard in Chrome app-window + tries fullscreen.
DIR="$(cd "$(dirname "$0")" && pwd)"
HTML="$DIR/index.html"

if [[ ! -f "$HTML" ]]; then
  osascript -e 'display alert "Dashboard not found" message "Keep this .command file in the same folder as index.html."'
  exit 1
fi

# Prefer Chrome; fall back to Safari
if [[ -d "/Applications/Google Chrome.app" ]]; then
  open -a "Google Chrome" --args --new-window --start-fullscreen "file://$HTML"
elif [[ -d "/Applications/Chromium.app" ]]; then
  open -a "Chromium" --args --new-window --start-fullscreen "file://$HTML"
else
  open -a "Safari" "file://$HTML"
  sleep 1
  osascript <<'AS'
tell application "Safari" to activate
tell application "System Events"
  keystroke "f" using {control down, command down}
end tell
AS
fi
