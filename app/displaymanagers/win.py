import cairo
import win32api
import win32con
import win32gui
import ctypes
import time
from ctypes import windll, Structure, byref

# Ensure the process is DPI aware for your 1920x1200 resolution
try:
    windll.shcore.SetProcessDpiAwareness(1)
except:
    windll.user32.SetProcessDPIAware()

# Tells Windows graphic system how to handle raw data of image
class BITMAPINFO(Structure):
    _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
                ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)]

class BLENDFUNCTION(Structure):
    _fields_ = [("BlendOp", ctypes.c_byte), ("BlendFlags", ctypes.c_byte),
                ("SourceConstantAlpha", ctypes.c_byte), ("AlphaFormat", ctypes.c_byte)]

class POINT(Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class SIZE(Structure):
    _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

class Manager:
    def __init__(self):
        # Auto-detects the full virtual screen size (handles multi-monitor setups)
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        self.hwnd = None
        self._create_window()
        
        # Pre-allocate resources to prevent lag and memory errors
        self.hdc_screen = win32gui.GetDC(self.hwnd)
        self.hdc_mem = windll.gdi32.CreateCompatibleDC(self.hdc_screen)
        self.ppvBits = ctypes.c_void_p()
        
        bi = BITMAPINFO(40, self.screen_width, -self.screen_height, 1, 32, 0, 0, 0, 0, 0, 0)
        self.hbmp = windll.gdi32.CreateDIBSection(self.hdc_mem, byref(bi), 0, byref(self.ppvBits), None, 0)
        windll.gdi32.SelectObject(self.hdc_mem, self.hbmp)

    def _create_window(self):
        # Fills out and registers a window template (WNDCLASS) so Windows knows how to build the overlay.
        class_name = "BruteForceOverlay"
        h_inst = win32api.GetModuleHandle(None)
        
        wnd_class = win32gui.WNDCLASS()
        wnd_class.lpfnWndProc = win32gui.DefWindowProc
        wnd_class.hInstance = h_inst
        wnd_class.lpszClassName = class_name
        try: win32gui.RegisterClass(wnd_class)
        except: pass

        # Create a basic Popup window with Topmost and Layered flags
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_TOPMOST | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT,
            class_name, "Overlay", win32con.WS_POPUP,
            0, 0, self.screen_width, self.screen_height, 0, 0, h_inst, None
        )
        
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    def start_draw(self):
        # Prepares a memory-backed ImageSurface for Cairo to draw on.
        # ARGB32 format is required for per-pixel alpha transparency.
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.screen_width, self.screen_height)
        return self.surface

    def stop_draw(self):
        # Ensures all pending Cairo drawing commands are written to the memory buffer
        self.surface.flush()
        
        # Get raw data from Cairo and move it into the allocated Win32 Bitmap memory
        surface_data = self.surface.get_data()
        ctypes.memmove(self.ppvBits, ctypes.c_char_p(surface_data.tobytes()), len(surface_data))
        
        # Configure Alpha Blending (255 = Opaque source, 1 = Use Alpha Channel)
        blend = BLENDFUNCTION(0, 0, 255, 1) 
        win_size = SIZE(self.screen_width, self.screen_height)
        src_pos = POINT(0, 0)
        
        # This function updates the window with the alpha-blended content directly
        # ULW_ALPHA (2) tells Windows to look at the pixel alpha values
        windll.user32.UpdateLayeredWindow(
            self.hwnd, self.hdc_screen, None, byref(win_size), self.hdc_mem, byref(src_pos), 0, byref(blend), 2
        )

        # Finalize the surface and process window messages
        self.surface.finish()
        win32gui.PumpWaitingMessages()

    def __del__(self):
        # Proper cleanup of permanent resources
        if self.hwnd:
            windll.gdi32.DeleteObject(self.hbmp)
            windll.gdi32.DeleteDC(self.hdc_mem)
            win32gui.ReleaseDC(self.hwnd, self.hdc_screen)

if __name__ == "__main__":
    m = Manager()
    print("Alpha Overlay active. Drawing semi-transparent red box...")
    
    try:
        # Loop for 100 frames (roughly 10 seconds at 0.1s sleep)
        for i in range(100):
            surf = m.start_draw()
            ctx = cairo.Context(surf)
            
            # Draw a RED box with 50% transparency (Alpha = 0.5)
            # The background remains 100% transparent without needing a color key
            ctx.set_source_rgba(1.0, 0.0, 0.0, 0.5) 
            w, h = 200, 200
            ctx.rectangle(m.screen_width//2 - w//2, m.screen_height//2 - h//2, w, h)
            ctx.fill()
            
            m.stop_draw()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")