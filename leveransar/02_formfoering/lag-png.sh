#!/bin/sh
# Bruk: sh lag-png.sh side-8-formfoering-sortiment   (lagar png/<namn>.png i 2254 x 1594)
D="C:/Users/Iver/Documents/github/GK5-modul_2/leveransar/02_formfoering"
P="C:/Users/Iver/AppData/Local/Temp/claude/9773ab2be0aca823/2c1f63c0-844c-4780-bd7e-44e5353e679d/scratchpad/chrome/$1"
mkdir -p "$P" "$D/png"
timeout 120 "/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --hide-scrollbars --no-first-run --user-data-dir="$P" --force-device-scale-factor=2 --window-size=1127,797 --default-background-color=000000ff --screenshot="$D/png/$1.png" "file:///$D/$1.html" 2>&1 | grep -i written
