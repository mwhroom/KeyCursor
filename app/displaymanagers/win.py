import cairo
import win32api
import win32con
import win32gui
import ctypes
from ctypes import windll, Structure, byref

# Define the BLENDFUNCTION structure required for Alpha Blending
class BLENDFUNCTION(Structure):
    _fields_ = [
        ("BlendOp", ctypes.c_byte),
        ("BlendFlags", ctypes.c_byte),
        ("SourceConstantAlpha", ctypes.c_byte),
        ("AlphaFormat", ctypes.c_byte),
    ]

# Required for creating a 32-bit (ARGB) memory buffer
class BITMAPINFOHEADER(Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_int32),
        ("biHeight", ctypes.c_int32),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_int32),
        ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]

class BITMAPINFO(Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", ctypes.c_uint32 * 3)]

class Manager:
    """
    Manager for a full-screen, click-through, transparent Cairo overlay.
    """
    def __init__(self):
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        self.window_handle = None
        self.hdc_screen = None
        self.hdc_mem = None
        self.hbitmap = None
        self.surface = None
        
        self._create_window()

    def _create_window(self):
        class_name = "CairoOverlayWindow"
        h_inst = win32api.GetModuleHandle(None)
        
        wnd_class = win32gui.WNDCLASS()
        wnd_class.lpfnWndProc = win32gui.DefWindowProc
        wnd_class.hInstance = h_inst
        wnd_class.lpszClassName = class_name
        
        try:
            win32gui.RegisterClass(wnd_class)
        except:
            pass # Already registered

        # WS_EX_LAYERED: Enables transparency
        # WS_EX_TRANSPARENT: Makes the window click-through
        # WS_EX_TOPMOST: Keeps it above all other windows
        self.window_handle = win32gui.CreateWindowEx(
            win32con.WS_EX_TOPMOST | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT,
            class_name, "Overlay", win32con.WS_POPUP,
            0, 0, self.screen_width, self.screen_height,
            0, 0, h_inst, None
        )
        
        win32gui.ShowWindow(self.window_handle, win32con.SW_SHOW)

    def start_draw(self):
        """
        Creates a back-buffer and returns a Cairo Win32Surface.
        """
        # 1. Get the screen DC and create a compatible memory DC
        self.hdc_screen = win32gui.GetDC(self.window_handle)
        self.hdc_mem = windll.gdi32.CreateCompatibleDC(self.hdc_screen)
        
        # 2. Define a 32-bit ARGB DIB (Device Independent Bitmap)
        # We use a negative height to ensure the bitmap is top-down (0,0 is top-left)
        bi = BITMAPINFO()
        bi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bi.bmiHeader.biWidth = self.screen_width
        bi.bmiHeader.biHeight = -self.screen_height 
        bi.bmiHeader.biPlanes = 1
        bi.bmiHeader.biBitCount = 32
        bi.bmiHeader.biCompression = 0 # BI_RGB

        self.hbitmap = windll.gdi32.CreateDIBSection(
            self.hdc_mem, byref(bi), 0, byref(ctypes.c_void_p()), None, 0
        )
        windll.gdi32.SelectObject(self.hdc_mem, self.hbitmap)
        
        # 3. Create the Cairo surface
        self.surface = cairo.Win32Surface(self.hdc_mem)
        
        # Clear the surface to be fully transparent initially
        ctx = cairo.Context(self.surface)
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.paint()
        
        return self.surface

    def stop_draw(self):
        """
        Flushes drawing to the window and performs resource cleanup.
        """
        if not self.surface:
            return

        self.surface.flush()

        # UpdateLayeredWindow parameters
        # AC_SRC_ALPHA (1) tells Windows to use the alpha channel in the bitmap
        blend = BLENDFUNCTION(0, 0, 255, 1) 
        pt_src = ctypes.c_longlong(0) # Represents a POINT structure at (0,0)
        
        windll.user32.UpdateLayeredWindow(
            self.window_handle, self.hdc_screen,
            None, None, # Use current window pos/size
            self.hdc_mem, byref(pt_src),
            0, byref(blend), 2 # 2 = ULW_ALPHA
        )

        # Resource Cleanup
        self.surface.finish() # Closes Cairo's handle on the DC
        windll.gdi32.DeleteObject(self.hbitmap)
        windll.gdi32.DeleteDC(self.hdc_mem)
        win32gui.ReleaseDC(self.window_handle, self.hdc_screen)
        
        self.surface = None