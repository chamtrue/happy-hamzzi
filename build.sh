#!/bin/bash
# art.py → frames/ → Hamster.app. 사용: ./build.sh
set -e; cd "$(dirname "$0")"
python3 art.py >/dev/null && python3 art32.py >/dev/null
APP="Happy Hamzzi.app"; rm -rf "$APP" Hamster.app; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp app/Info.plist "$APP/Contents/"; cp app/AppIcon.icns "$APP/Contents/Resources/"
cp -R frames "$APP/Contents/Resources/"
swiftc -O -framework AppKit -framework EventKit -framework IOKit -framework CoreLocation -framework SwiftUI -framework ServiceManagement app/main.swift -o "$APP/Contents/MacOS/hamster"
codesign -s "Happy Hamzzi Dev" --force --deep "$APP" 2>/dev/null || codesign -s - --force --deep "$APP" >/dev/null 2>&1
echo "built $APP"
if [ "$1" = "install" ]; then
  pkill -f "Happy Hamzzi.app/Contents/MacOS/hamster" 2>/dev/null; sleep 0.5
  rm -rf "/Applications/$APP"; cp -R "$APP" /Applications/ && open "/Applications/$APP" && echo "installed /Applications/$APP"
fi
