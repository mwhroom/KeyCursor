import pydotool
from pydotool import ClickEnum as ce
pydotool.init()

class Manager:
    def __init__(self, displaymanager):
        self.rough_cursor_pos = [displaymanager.screen_width//2, displaymanager.screen_height//2]
        pydotool.mouse_move(tuple(self.rough_cursor_pos), True)
    

    def move(self, x:int, y:int):
        if not x and not y:
            return
        self.rough_cursor_pos[0] += x
        self.rough_cursor_pos[1] += y
        pydotool.mouse_move((x, y))

    
    def scroll(self, x:int, y:int):
        pydotool.wheel_move(x, y)
    

    def get_pos(self):
        pydotool.mouse_move(tuple(self.rough_cursor_pos), True)
        return tuple(self.rough_cursor_pos)


    def set_pos(self, x:int, y:int):
        self.rough_cursor_pos = [x, y]
        pydotool.mouse_move((x, y), True)


    # button = 0: left, 1: right, 2: middle
    def click(self, button:int, count:int=1):
        pydotool.click_sequence([button|ce.MOUSE_DOWN, 
                                 button|ce.MOUSE_UP] * count)


    # button = 0: left, 1: right, 2: middle
    def press(self, button:int):
        pydotool.click_sequence(button|ce.MOUSE_DOWN)


    # button = 0: left, 1: right, 2: middle
    def release(self, button:int):
        pydotool.click_sequence(button|ce.MOUSE_UP)
    
if __name__=='__main__':
    from time import sleep
    while True:
        pydotool.mouse_move((-100, 100))
        sleep(.1)
