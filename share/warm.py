#!/usr/bin/python
import json, os, signal, sys
from pathlib import Path
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gio

sys.path.insert(0, str(Path.home() / ".local/share/instant-window"))
import placeholder as ph  # reuse find_icon only

PID = os.getpid()
APP_ID = f"com.local.instantplaceholder.w{PID}"
DATA = Path(f"/tmp/instant-warm-{PID}.json")


class Warm(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=0)

    def do_activate(self):
        self.win = Gtk.ApplicationWindow(application=self)
        self.win.set_title("Warm placeholder")
        self.win.set_default_size(600, 400)
        self.win.set_decorated(False)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        self.image = Gtk.Image()
        self.image.set_pixel_size(96)
        spinner = Gtk.Spinner()
        spinner.set_size_request(36, 36)
        spinner.start()
        self.title = Gtk.Label(label="Closing")
        self.title.add_css_class("title-1")
        self.title.set_ellipsize(3)
        self.title.set_max_width_chars(40)
        sub = Gtk.Label(label="Closing your workspace…")
        sub.add_css_class("dim-label")
        for w in (self.image, spinner, self.title, sub):
            box.append(w)
        self.win.set_child(box)

        css = Gtk.CssProvider()
        css.load_from_data(b"""
            window { background-color: #17191f; color: #f1f3f9; }
            label { color: #f1f3f9; }
            .title-1 { font-size: 24px; font-weight: 600; }
            .dim-label { color: #9ba3b4; font-size: 14px; }
        """)
        Gtk.StyleContext.add_provider_for_display(
            self.win.get_display(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.win.present()
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, self.refresh)

    def refresh(self, *a):
        try:
            d = json.loads(DATA.read_text())
        except Exception:
            return True
        name, hint = d.get("name", ""), d.get("hint", "")
        self.title.set_label(f"Closing {name}")
        icon = ph.find_icon(hint, name)
        theme = Gtk.IconTheme.get_for_display(self.win.get_display())
        if icon.startswith("/") and os.path.isfile(icon):
            self.image.set_from_gicon(Gio.FileIcon.new(Gio.File.new_for_path(icon)))
        elif icon and theme.has_icon(icon):
            self.image.set_from_icon_name(icon)
        else:
            self.image.set_from_icon_name("application-x-executable")
        return True


if __name__ == "__main__":
    try:
        raise SystemExit(Warm().run([]))
    finally:
        try:
            DATA.unlink()
        except OSError:
            pass
