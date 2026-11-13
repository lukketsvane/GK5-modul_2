#!/bin/sh
# Bruk: sh lag-png.sh side-3-3b-analyse   (lagar png/<namn>.png i 2254 x 1594)
D="C:/Users/Iver/Documents/github/GK5-modul_2/leveransar/01_fase1_sider"
timeout 45 "/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --window-size=1127,797 --screenshot="$D/png/$1.png" "file:///$D/$1.html" 2>&1 | grep -i written
