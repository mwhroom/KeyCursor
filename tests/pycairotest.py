#!/usr/bin/env python

import testglobal

import time
import math
import threading
import random

import cairo
import win32api, win32con, win32gui

screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

class MyWindow:
    def __init__(self):
        self.main_thread = threading.Thread(target=self.main_loop)

        win32gui.InitCommonControls()

        # Get module handle instance
        self.hinst = win32api.GetModuleHandle(None)

        # Set name of class
        className = 'Window Test'

        # Create window class
        wc = win32gui.WNDCLASS()
        #wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = className
        wc.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)

        # Register class in windows
        win32gui.RegisterClass(wc)

        style = win32con.WS_EX_LAYERED|win32con.WS_EX_TRANSPARENT|win32con.WS_MAXIMIZE|win32con.WS_POPUPWINDOW
        print(f'{style:b}')

        # Create window handle
        self.hwnd = win32gui.CreateWindow(
            className, # Class
            'Testing the creation of a window with pycairo graphics.', # Description
            style,
            win32con.CW_USEDEFAULT, # x pos
            win32con.CW_USEDEFAULT, # y pos
            screen_width, # Size x
            screen_height, # Size y
            None, # Parent
            None, # Menu
            self.hinst, # Module handle instance
            None # Extra creation parameters
        )
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, style)

        # Make window always stay on top
        
        
        win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(255, 255, 255), 0, win32con.LWA_COLORKEY)

        win32gui.SetWindowPos(
            self.hwnd,
            win32con.HWND_TOPMOST,  # Place the window at the top of the Z order
            0, 0, 0, 0,             # No change to x, y, width, or height (params are ignored due to flags)
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_FRAMECHANGED
        )

        

        # Update and show window
        self.draw_image()
        win32gui.UpdateWindow(self.hwnd)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

        # Start main thread
        self.main_thread.start()

    # When the X button is clicked, or window is destroyed in any way
    def OnDestroy(self, hwnd, message, wparam, lparam):
        print("attempting to close")
        self.stop_main()
        win32gui.PostQuitMessage(0)
        return True

    def stop_main(self):
        print("stopping main")
        self.main_thread.stop()
        self.main_thread.join()
        print("main stopped")

    # Window process
    # Manage all processes, such as paint calls, input events, etc.
    # Inputs: Window obj, window handle, type of update, wparam for specific msg, lparam for specific msg
    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_PAINT:
            self.on_paint()
        elif msg == win32con.WM_DESTROY:
            return self.OnDestroy(hwnd, msg, wparam, lparam)
        elif msg == win32con.WM_CLOSE:
            win32gui.DestroyWindow(self.hwnd)
            self.stop_main()
        elif msg == win32con.WM_QUIT:
            self.stop_main()
        elif msg == win32con.WM_ERASEBKGND:
            print('tried to erase')
        return 0

    #User defined function, do action when paint process is called
    def on_paint(self):
        pass

    def main_loop(self):
        while 1:
            time.sleep(1/30) # 30 fps
            #print("time to draw!")
            # failed attempt to make windows redraw the background, just handle it manually
            # win32gui.RedrawWindow(self.hwnd, None, None, win32con.RDW_INVALIDATE|win32con.RDW_ERASE)
            if random.random()>=.5:
                testglobal.position[0]+=random.randrange(1, 10)
            else:
                testglobal.position[1]+=random.randrange(1, 10)
            self.draw_image()
        

    def draw_image(self):
        # Device context handle (in this case, the window)
        hdc = win32gui.GetDC(self.hwnd)
        
        # Normal imp: 
        # surface = cairo.ImageSurface(cairo.FORMAT_WIN32_SURFACE, WIDTH, HEIGHT)
        # Win specific imp:
        surface = cairo.Win32Surface(hdc)

        ctx = cairo.Context(surface)

        ctx.scale(1, 1)  # Normalizing the canvas

        ctx.set_antialias(cairo.ANTIALIAS_NONE) # No antialiasing

        # create pattern
        # edited to just fill with white
        pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
        pat.add_color_stop_rgba(1, 1, 1, 1, 1)  # First stop, 50% opacity
        pat.add_color_stop_rgba(1, 1, 1, 1, 1)  # Last stop, 0% opacity

        # set pattern as background
        ctx.rectangle(0, 0, screen_width, screen_height)  # Rectangle(x0, y0, x1, y1)
        ctx.set_source(pat)
        ctx.fill()

        rad = 20
        if testglobal.position[0]>=screen_width+rad:
            testglobal.position[0] = -rad
        if testglobal.position[1]>=screen_height+rad:
            testglobal.position[1] = -rad

        ctx.translate(testglobal.position[0], testglobal.position[1])  # Changing the current transformation matrix

        # Arc(cx, cy, radius, start_angle, stop_angle)
        #ctx.arc(0.2, 0.1, 0.1, -math.pi / 2, 0)
        #ctx.line_to(0.5+time.process_time(), 0.1)  # Line to (x,y)
        # Curve(x1, y1, x2, y2, x3, y3)
        #ctx.curve_to(0.5, 0.2, 0.5, 0.4, 0.2, 0.8)
        #ctx.close_path()
        ctx.arc(0.0, 0.0, rad, 0.0, 2.0*math.pi)
        ctx.close_path()
        ctx.set_source_rgba(0.0, 0.0, .7, .5)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.3, 0.3, 0.3)  # Solid color
        ctx.set_line_width(4)
        ctx.stroke()
        
        surface.flush()

        # Release device context handle to be used somewhere else
        # Similar to freeing
        win32gui.ReleaseDC(self.hwnd, hdc)



if __name__=="__main__":
    w = MyWindow()
    random.seed(time.time())

    win32gui.PumpMessages()



