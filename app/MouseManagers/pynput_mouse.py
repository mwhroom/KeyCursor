from pynput.mouse import Controller, Button
class Manager:
    def __init__(self):
        self.controller = Controller()
    
    def move(self, x:int, y:int):
        self.controller.move(x, y)
    
    def set_pos(self, x:int, y:int):
        self.controller.position = (x, y)
    
    # button = 0: left, 1: right, 2: middle
    def click(self, button:int, count:int=1):
        match button:
            case 0:
                self.controller.click(Button.left, count)
            case 1:
                self.controller.click(Button.right, count)
            case 2:
                self.controller.click(Button.middle, count)
    
