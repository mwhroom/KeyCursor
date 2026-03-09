from pynput.mouse import Controller, Button
class Manager:
    def __init__(self):
        self.controller = Controller()
    

    def move(self, x:int, y:int):
        self.controller.move(x, y)

    
    def scroll(self, x:int, y:int):
        self.controller.scroll(x, y)
    

    def get_pos(self):
        return self.controller.position


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
    

    # button = 0: left, 1: right, 2: middle
    def press(self, button:int):
        match button:
            case 0:
                self.controller.press(Button.left)
            case 1:
                self.controller.press(Button.right)
            case 2:
                self.controller.press(Button.middle)


    # button = 0: left, 1: right, 2: middle
    def release(self, button:int):
        match button:
            case 0:
                self.controller.release(Button.left)
            case 1:
                self.controller.release(Button.right)
            case 2:
                self.controller.release(Button.middle)
    
