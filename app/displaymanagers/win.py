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

class BITMAPINFO(Structure):
    _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
                ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)]

class Manager:
    def __init__(self):
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        
        # We'll use Magenta as our "invisible" color
        self.key_color = win32api.RGB(255, 0, 255) 
        self.hwnd = None
        self._create_window()

    def _create_window(self):
        class_name = "BruteForceOverlay"
        h_inst = win32api.GetModuleHandle(None)
        
        wnd_class = win32gui.WNDCLASS()
        wnd_class.lpfnWndProc = win32gui.DefWindowProc
        wnd_class.hInstance = h_inst
        wnd_class.lpszClassName = class_name
        try: win32gui.RegisterClass(wnd_class)
        except: pass

        # Create a basic Popup window
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_TOPMOST | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT,
            class_name, "Overlay", win32con.WS_POPUP,
            0, 0, self.screen_width, self.screen_height, 0, 0, h_inst, None
        )

        # THE CRITICAL LINE: Tell Windows to punch a hole through the key_color
        # 0x000001 is LWA_COLORKEY
        win32gui.SetLayeredWindowAttributes(self.hwnd, self.key_color, 0, 0x000001)
        
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    def start_draw(self):
        """Prepares a memory DC for Cairo to draw on."""
        self.hdc_screen = win32gui.GetDC(self.hwnd)
        self.hdc_mem = windll.gdi32.CreateCompatibleDC(self.hdc_screen)
        
        # Standard 32-bit bitmap
        bi = BITMAPINFO(40, self.screen_width, -self.screen_height, 1, 32, 0, 0, 0, 0, 0, 0)
        self.hbmp = windll.gdi32.CreateDIBSection(self.hdc_mem, byref(bi), 0, byref(ctypes.c_void_p()), None, 0)
        windll.gdi32.SelectObject(self.hdc_mem, self.hbmp)
        
        self.surface = cairo.Win32Surface(self.hdc_mem)
        ctx = cairo.Context(self.surface)
        
        # IMPORTANT: Fill the entire background with our "Invisible Pink"
        # Cairo uses 0.0-1.0 range. Magenta is (1.0, 0.0, 1.0)
        ctx.set_source_rgb(1.0, 0.0, 1.0)
        ctx.paint()
        
        return self.surface

    def stop_draw(self):
        """Blits the memory buffer to the screen."""
        self.surface.flush()
        
        # Copy the memory buffer to the window's real device context
        win32gui.BitBlt(self.hdc_screen, 0, 0, self.screen_width, self.screen_height, 
                        self.hdc_mem, 0, 0, win32con.SRCCOPY)

        # Cleanup
        self.surface.finish()
        windll.gdi32.DeleteObject(self.hbmp)
        windll.gdi32.DeleteDC(self.hdc_mem)
        win32gui.ReleaseDC(self.hwnd, self.hdc_screen)
        
        # Process window messages so Windows doesn't think the app is frozen
        win32gui.PumpWaitingMessages()

if __name__ == "__main__":
    m = Manager()
    print("Overlay active. Drawing red box...")
    
    try:
        # Loop for 10 seconds
        for i in range(100):
            surf = m.start_draw()
            ctx = cairo.Context(surf)
            
            # Draw a solid RED box in the center
            ctx.set_source_rgb(1.0, 0.0, 0.0)
            w, h = 200, 200
            ctx.rectangle(m.screen_width//2 - w//2, m.screen_height//2 - h//2, w, h)
            ctx.fill()
            
            m.stop_draw()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass