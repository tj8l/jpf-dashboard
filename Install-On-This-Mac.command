#!/bin/bash
# JPF Dashboard — one-time Mac installer (run with Right-click → Open)
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Documents/JPF-Dashboard"
mkdir -p "$DEST"

echo "Installing to: $DEST"

# Copy dashboard files from this package
for f in index.html data.json calendar.json weather.json markets.json; do
  if [[ -f "$SRC/$f" ]]; then
    cp -f "$SRC/$f" "$DEST/$f"
    echo "  copied $f"
  else
    echo "  MISSING $f (needed next to this installer)"
  fi
done

if [[ ! -f "$DEST/index.html" ]]; then
  osascript -e 'display alert "JPF Dashboard" message "index.html was not found next to Install-On-This-Mac.command. Unzip the whole package, then run the installer again."'
  exit 1
fi

APP="$DEST/JPF Dashboard.app"
rm -rf "$APP"

# Build a native AppleScript app (created on this Mac → far fewer Gatekeeper fights)
osacompile -o "$APP" <<'APPLESCRIPT'
set dashFolder to (POSIX path of (path to documents folder)) & "JPF-Dashboard/"
set htmlPath to dashFolder & "index.html"

set htmlExists to do shell script "test -f " & quoted form of htmlPath & " && echo yes || echo no"
if htmlExists is "no" then
  display alert "JPF Dashboard" message "Missing index.html in Documents/JPF-Dashboard. Re-run Install-On-This-Mac.command."
  return
end if

set fileURL to "file://" & htmlPath

-- Prefer Chrome app-mode window (clean board, no tab chrome). Falls back to Safari.
set chromeApp to "/Applications/Google Chrome.app"
set chromeExists to do shell script "test -d " & quoted form of chromeApp & " && echo yes || echo no"

if chromeExists is "yes" then
  -- open -na + --app reliably opens a dedicated window even if Chrome is already running
  do shell script "open -na " & quoted form of "Google Chrome" & " --args --new-window --app=" & quoted form of fileURL
else
  do shell script "open -a Safari " & quoted form of fileURL
  delay 1.2
  try
    tell application "Safari" to activate
    tell application "System Events" to keystroke "f" using {control down, command down}
  end try
end if
APPLESCRIPT

# Clear quarantine so Login Items / double-click work
xattr -cr "$DEST" 2>/dev/null || true
xattr -cr "$APP" 2>/dev/null || true

# Smoke-test open once
open "$APP" || true

# Jump to Login Items (Ventura+)
open "x-apple.systempreferences:com.apple.LoginItems-Settings.extension" 2>/dev/null || \
  open "/System/Library/PreferencePanes/Users.prefPane" 2>/dev/null || true

osascript <<'DONE'
display alert "JPF Dashboard installed" message "1) System Settings → Login Items should be open — click + and add “JPF Dashboard”.
2) Folder: Documents/JPF-Dashboard
3) Test: double-click JPF Dashboard.app there anytime.

Chrome app-mode opens the board. Leave that window open to keep it up."
DONE

echo "Done."
