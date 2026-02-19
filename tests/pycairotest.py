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

        # this is required for some reason even though we already create the window with the style
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, style) 
        
        # key white out to be a transparent color
        win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(255, 255, 255), 0, win32con.LWA_COLORKEY)

        # Make window always stay on top
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

    # Stop main thread
    def stop_main(self):
        print("stopping main")
        self.main_thread.stop()
        self.main_thread.join()
        print("main stopped")

    # Window process
    # Manage all processes, such as paint calls, input events, etc.
    # Inputs: Window obj, window handle, type of update, wparam for specific msg, lparam for specific msg
    def wnd_proc(self, hwnd, msg, wparam, lparam):
        # Called every paint frame (a lot)
        if msg == win32con.WM_PAINT:
            self.on_paint()
        
        # Idk what the rest of these do, can't seem to make them work
        elif msg == win32con.WM_DESTROY:
            self.stop_main()
            win32gui.PostQuitMessage(0)
            return True
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

    # Main loop on separate thread
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
        

    # draw the circle
    def draw_image(self):
        # Device context handle (in this case, the window)
        hdc = win32gui.GetDC(self.hwnd)
        
        # Normal imp: 
        # surface = cairo.ImageSurface(cairo.FORMAT_WIN32_SURFACE, WIDTH, HEIGHT)
        # Win specific imp:
        surface = cairo.Win32Surface(hdc) # create cairo surface

        ctx = cairo.Context(surface) # create cairo context on surface
        ctx.set_antialias(cairo.ANTIALIAS_NONE) # No antialiasing

        # create pattern
        # edited code to just fill with white
        pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
        pat.add_color_stop_rgba(1, 1, 1, 1, 1)  # First stop, 50% opacity
        pat.add_color_stop_rgba(1, 1, 1, 1, 1)  # Last stop, 0% opacity

        # set pattern as background
        ctx.rectangle(0, 0, screen_width, screen_height)  # Rectangle(x0, y0, x1, y1)
        ctx.set_source(pat)
        ctx.fill()

        # make circle pos loop screen
        rad = 20
        if testglobal.position[0]>=screen_width+rad:
            testglobal.position[0] = -rad
        if testglobal.position[1]>=screen_height+rad:
            testglobal.position[1] = -rad

        # set relative position
        ctx.translate(testglobal.position[0], testglobal.position[1])

        # draw circle
        ctx.arc(0.0, 0.0, rad, 0.0, 2.0*math.pi)
        ctx.close_path()
        ctx.set_source_rgba(0.0, 0.0, .7, .5)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.3, 0.3, 0.3)
        ctx.set_line_width(4)
        ctx.stroke()
        
        # flush surface (must be done at end of every drawing)
        surface.flush()

        # Release device context handle to be used somewhere else
        # Similar to freeing
        win32gui.ReleaseDC(self.hwnd, hdc)



if __name__=="__main__":
    w = MyWindow()
    random.seed(time.time())
    win32gui.PumpMessages()