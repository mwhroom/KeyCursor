import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")

from gi.repository import Gtk, GLib, Gdk, GtkLayerShell
import threading
import cairo


class Manager(Gtk.Window):
    def __init__(self):
        super().__init__()

        # Layer shell setup
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)

        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

        GtkLayerShell.set_exclusive_zone(self, -1)

        self.display = Gdk.Display.get_default()
        self.monitor = self.display.get_monitor(0)
        self.screen_size = self.monitor.get_geometry()
        self.screen_width = self.screen_size.width
        self.screen_height = self.screen_size.height

        self.surface_changed = False
        self.portable_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.screen_width, self.screen_height)

        self.set_app_paintable(True)
        self.set_default_size(self.screen_width, self.screen_height)
        
        self.connect("draw", self.on_draw)
        self.connect("destroy", Gtk.main_quit)

        self.show()

        self.main_thread = threading.Thread(target = Gtk.main)
        self.main_thread.start()


    def tick(self):
        self.queue_draw()
        return True


    def clear_screen(self):
        ctx = cairo.Context(self.portable_surface)
        ctx.rectangle(0, 0, self.screen_width, self.screen_height)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        ctx.fill()
        self.surface_changed = True


    def on_draw(self, widget, ctx: cairo.Context):
        if self.surface_changed:
            ctx.set_source_surface(self.portable_surface, self.screen_width, self.screen_height)
            self.surface_changed = False


    def go_to_bottom(self):
        GLib.idle_add(GtkLayerShell.set_layer, 
                      self,
                      GtkLayerShell.Layer.BOTTOM)


    def go_to_top(self):
        GLib.idle_add(GtkLayerShell.set_layer, 
                      self,
                      GtkLayerShell.Layer.OVERLAY)


    def start_draw(self):
        return self.portable_surface


    def stop_draw(self):
        self.portable_surface.flush()
        self.surface_changed = True


    def __del__(self):
        GLib.idle_add(Gtk.main_quit)
