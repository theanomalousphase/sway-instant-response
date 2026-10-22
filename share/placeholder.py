#!/usr/bin/python
import os
import sys
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Gio
from pathlib import Path

app_name = sys.argv[1] if len(sys.argv) > 1 else "application"
action = sys.argv[2] if len(sys.argv) > 2 else "Opening"
app_id = f"com.local.instantplaceholder.p{os.getpid()}"

if action not in ("Opening", "Closing"):
    action = "Opening"

subtitle_text = (
    "Preparing your workspace…"
    if action == "Opening"
    else "Closing your workspace…"
)

try:
    width = max(1, int(sys.argv[3]))
    height = max(1, int(sys.argv[4]))
except (IndexError, ValueError):
    width, height = 520, 300

try:
    x = int(sys.argv[5])
    y = int(sys.argv[6])
except (IndexError, ValueError):
    x = y = None


DESKTOP_DIRS = [
    Path("/usr/share/applications"),
    Path.home() / ".local/share/applications",
    Path("/var/lib/flatpak/exports/share/applications"),
    Path.home() / ".local/share/flatpak/exports/share/applications",
]


def find_icon(*hints):
    wanted = {h.strip().lower() for h in hints if h and h.strip()}
    if not wanted:
        return ""
    for d in DESKTOP_DIRS:
        if not d.is_dir():
            continue
        for f in d.glob("*.desktop"):
            keys = {f.stem.lower()}
            icon = ""
            in_entry = False
            try:
                for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if line.startswith("["):
                        in_entry = line == "[Desktop Entry]"
                    elif in_entry and line.startswith("Name="):
                        keys.add(line[5:].strip().lower())
                    elif in_entry and line.startswith("StartupWMClass="):
                        keys.add(line[15:].strip().lower())
                    elif in_entry and line.startswith("Icon="):
                        icon = line[5:].strip()
            except OSError:
                continue
            if icon and keys & wanted:
                return icon
    return ""


class Placeholder(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=app_id, flags=0)

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title(f"{action} {app_name}")
        window.set_default_size(width, height)
        window.set_decorated(False)
        if len(sys.argv) > 4:
            window.set_resizable(False)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        spinner = Gtk.Spinner()
        spinner.set_size_request(36, 36)
        spinner.start()

        title = Gtk.Label(label=f"{action} {app_name}")
        title.add_css_class("title-1")
        title.set_ellipsize(3)
        title.set_max_width_chars(40)

        subtitle = Gtk.Label(label=subtitle_text)
        subtitle.add_css_class("dim-label")

        box.append(spinner)
        box.append(title)
        box.append(subtitle)

        image = Gtk.Image()
        image.set_pixel_size(96)
        box.prepend(image)
        window.set_child(box)

        css = Gtk.CssProvider()
        css.load_from_data(b"""
            window { background-color: #17191f; color: #f1f3f9; }
            label { color: #f1f3f9; }
            .title-1 { font-size: 24px; font-weight: 600; }
            .dim-label { color: #9ba3b4; font-size: 14px; }
        """)
        Gtk.StyleContext.add_provider_for_display(
            window.get_display(), css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        window.present()

        def load_icon():
            icon = find_icon(os.environ.get("INSTANT_ICON_HINT", ""), app_name)
            theme = Gtk.IconTheme.get_for_display(window.get_display())
            if icon.startswith("/") and os.path.isfile(icon):
                image.set_from_gicon(Gio.FileIcon.new(Gio.File.new_for_path(icon)))
            elif icon and theme.has_icon(icon):
                image.set_from_icon_name(icon)
            else:
                image.set_from_icon_name("application-x-executable")
            return False

        GLib.idle_add(load_icon)

        # GTK4/Wayland does not provide a portable API for arbitrary
        # top-level window positioning. Sway will handle placement.
        if x is not None and y is not None:
            pass


if __name__ == "__main__":
    raise SystemExit(Placeholder().run([]))
