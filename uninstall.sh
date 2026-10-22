#!/bin/bash
pkill -f warm.py 2>/dev/null
rm -f ~/.local/bin/instant-close ~/.local/bin/instant-launch
rm -rf ~/.local/share/instant-window
echo "Removed. Delete the instant-window lines from ~/.config/sway/config and run: swaymsg reload"
