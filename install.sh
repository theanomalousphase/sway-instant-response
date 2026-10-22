#!/bin/bash
set -e
R="$(cd "$(dirname "$0")" && pwd)"
for c in swaymsg python wofi gtk-launch; do
  command -v $c >/dev/null || { echo "Missing: $c (Arch: sudo pacman -S sway python python-gobject gtk4 wofi)"; exit 1; }
done
python -c "import gi; gi.require_version('Gtk','4.0')" 2>/dev/null || { echo "Missing: python-gobject / gtk4"; exit 1; }
mkdir -p ~/.local/bin ~/.local/share/instant-window
cp "$R"/bin/* ~/.local/bin/ && chmod +x ~/.local/bin/instant-close ~/.local/bin/instant-launch
cp "$R"/share/* ~/.local/share/instant-window/
cat <<'CFG'

Installed. Add these lines to ~/.config/sway/config, then run: swaymsg reload

bindsym $mod+d exec ~/.local/bin/instant-launch
bindsym $mod+q exec ~/.local/bin/instant-close
for_window [app_id="^com\.local\.instantplaceholder\.w[0-9]+$"] floating enable, border none, opacity 0, move container to workspace number 9
for_window [app_id="^com\.local\.instantplaceholder\." title="^Closing "] opacity 0
exec /usr/bin/python ~/.local/share/instant-window/warm.py
CFG
