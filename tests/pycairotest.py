#!/usr/bin/env python

import math
import cairo
import win32api, win32con, win32gui

WIDTH, HEIGHT = 256, 256

class MyWindow:
    def __init__(self):
        win32gui.InitCommonControls()

        # Get module handle instance
        self.hinst = win32api.GetModuleHandle(None)

        # Set name of class
        className = 'Window Test'

        # Create window class
        wc = win32gui.WNDCLASS()
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = className

        # Register class in windows
        win32gui.RegisterClass(wc)


        style = win32con.WS_OVERLAPPEDWINDOW

        # Create window handle
        self.hwnd = win32gui.CreateWindow(
            className, # Class
            'Testing the creation of a window with pycairo graphics.', # Description
            style,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            500, # Size x
            500, # Size y
            0, # IDK
            0, # IDK
            self.hinst, # Module handle instance
            None # I dont even know
        )

        # Update and show window
        win32gui.UpdateWindow(self.hwnd)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    # When the X button is clicked, or window is destroyed in any way
    def OnDestroy(self, hwnd, message, wparam, lparam):
        win32gui.PostQuitMessage(0)
        return True

    # Window process
    # Manage all processes, such as paint calls, input events, etc.
    # Inputs: Window obj, window handle, type of update, wparam for specific msg, lparam for specific msg
    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_PAINT:
            self.on_paint()
        elif msg == win32con.WM_DESTROY:
            self.OnDestroy(hwnd, msg, wparam, lparam)
        return 0

    #User defined function, do action when paint process is called
    def on_paint(self):
        # Device context handle (in this case, the window)
        hdc = win32gui.GetDC(self.hwnd)
        
        # Normal imp: surface = cairo.ImageSurface(cairo.FORMAT_WIN32_SURFACE, WIDTH, HEIGHT)
        # Win specific imp:
        surface = cairo.Win32Surface(hdc)

        ctx = cairo.Context(surface)

        ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas

        pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
        pat.add_color_stop_rgba(1, 0.7, 0, 0, 0.5)  # First stop, 50% opacity
        pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity

        ctx.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)
        ctx.set_source(pat)
        ctx.fill()

        ctx.translate(0.1, 0.1)  # Changing the current transformation matrix

        ctx.move_to(0, 0)
        # Arc(cx, cy, radius, start_angle, stop_angle)
        ctx.arc(0.2, 0.1, 0.1, -math.pi / 2, 0)
        ctx.line_to(0.5, 0.1)  # Line to (x,y)
        # Curve(x1, y1, x2, y2, x3, y3)
        ctx.curve_to(0.5, 0.2, 0.5, 0.4, 0.2, 0.8)
        ctx.close_path()

        ctx.set_source_rgb(0.3, 0.2, 0.5)  # Solid color
        ctx.set_line_width(0.02)
        ctx.stroke()
        
        surface.flush()

        # Release device context handle to be used somewhere else
        win32gui.ReleaseDC(self.hwnd, hdc)


if __name__=="__main__":
    w = MyWindow()
    win32gui.PumpMessages()



