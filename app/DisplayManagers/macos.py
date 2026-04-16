import cairo
import threading

from AppKit import (
    NSApplication, NSWindow, NSScreen,
    NSColor, NSBorderlessWindowMask, NSBackingStoreBuffered,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
    NSWindowCollectionBehaviorIgnoresCycle,
    NSRunLoop, NSDefaultRunLoopMode, NSDate,
)
from Foundation import NSData, NSMakeSize
from Quartz import (
    CALayer, CATransaction,
    CGImageCreate, CGDataProviderCreateWithCFData,
    CGColorSpaceCreateDeviceRGB,
    kCGBitmapByteOrder32Little, kCGImageAlphaPremultipliedFirst,
    kCGRenderingIntentDefault,
)

# Screen saver level (1000) places the overlay above all normal app windows.
_OVERLAY_WINDOW_LEVEL = 1000


class Manager:
    def __init__(self):
        self.app = NSApplication.sharedApplication()
        # NSApplicationActivationPolicyAccessory: no Dock icon, no menu bar
        self.app.setActivationPolicy_(2)

        screen = NSScreen.mainScreen()
        frame  = screen.frame()
        self.screen_width  = int(frame.size.width)
        self.screen_height = int(frame.size.height)

        # Borderless, transparent, click-through window covering the full screen
        self._window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSBorderlessWindowMask,
            NSBackingStoreBuffered,
            False,
        )
        self._window.setBackgroundColor_(NSColor.clearColor())
        self._window.setOpaque_(False)
        self._window.setIgnoresMouseEvents_(True)
        self._window.setLevel_(_OVERLAY_WINDOW_LEVEL)
        self._window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces   # visible on every Space
            | NSWindowCollectionBehaviorStationary       # stays put during Exposé
            | NSWindowCollectionBehaviorIgnoresCycle     # excluded from Cmd-Tab
        )
        self._window.setHasShadow_(False)

        # Use an explicit CALayer for pixel updates.
        # Setting the layer before setWantsLayer_ makes it "explicit" rather
        # than a backing layer managed by AppKit — more predictable behavior
        # when updating from a background thread.
        content_view = self._window.contentView()
        self._layer = CALayer.layer()
        self._layer.setOpaque_(False)
        content_view.setLayer_(self._layer)
        content_view.setWantsLayer_(True)

        self._window.orderFrontRegardless()

        self.surface = None

        # The input manager blocks the main thread with listener.join(), so we
        # run the AppKit event loop on a background thread to keep the window
        # alive — same pattern as the GTK backend's Gtk.main() thread.
        self._app_thread = threading.Thread(target=self.app.run, daemon=True)
        self._app_thread.start()


    def start_draw(self) -> cairo.ImageSurface:
        """Allocate a fresh Cairo surface and return it for drawing."""
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.screen_width, self.screen_height
        )
        ctx = cairo.Context(self.surface)
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        return self.surface


    def stop_draw(self):
        """Push the finished Cairo surface to the overlay window."""
        self.surface.flush()

        # Cairo ARGB32 pixels are 0xAARRGGBB in native (little-endian) byte
        # order — bytes on disk are [B, G, R, A].  The CGImage flags below
        # declare exactly that layout, so no conversion is needed.
        #
        # NSData copies the bytes and CGDataProviderCreateWithCFData retains
        # the NSData via CFRetain, so the buffer stays alive for the CGImage's
        # full lifetime with no manual tracking needed.
        raw      = self.surface.get_data()
        ns_data  = NSData.dataWithBytes_length_(bytes(raw), len(raw))
        provider = CGDataProviderCreateWithCFData(ns_data)

        cg_image = CGImageCreate(
            self.screen_width,
            self.screen_height,
            8,                          # bits per component
            32,                         # bits per pixel
            self.screen_width * 4,      # bytes per row
            CGColorSpaceCreateDeviceRGB(),
            kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedFirst,
            provider,
            None,                       # no decode array
            False,                      # no interpolation
            kCGRenderingIntentDefault,
        )

        # Wrap in a CATransaction so the update is flushed to the render server
        # immediately, even when called from a background thread with no run loop.
        CATransaction.begin()
        CATransaction.setDisableActions_(True)  # no implicit animation
        self._layer.setContents_(cg_image)
        CATransaction.commit()
        CATransaction.flush()

        self.surface.finish()


    def clear_screen(self):
        self.start_draw()
        self.stop_draw()


    def __del__(self):
        pass


# ---------------------------------------------------------------------------
# Quick smoke-test: draws a semi-transparent red rectangle for ~10 seconds.
# Run with:  python3 DisplayManagers/macos.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    m = Manager()
    print(f"Overlay active ({m.screen_width}x{m.screen_height}). Drawing red box…")

    try:
        for i in range(100):
            surf = m.start_draw()
            ctx  = cairo.Context(surf)
            ctx.set_source_rgba(1.0, 0.0, 0.0, 0.5)
            w, h = 200, 200
            ctx.rectangle(
                m.screen_width  // 2 - w // 2 + i,
                m.screen_height // 2 - h // 2,
                w, h,
            )
            ctx.fill()
            m.stop_draw()

            # Pump the main run loop for 0.1 s — keeps the window visible and
            # processes any window-server events while the smoke test runs.
            NSRunLoop.mainRunLoop().runMode_beforeDate_(
                NSDefaultRunLoopMode,
                NSDate.dateWithTimeIntervalSinceNow_(0.1),
            )
    except KeyboardInterrupt:
        print("Stopping…")
