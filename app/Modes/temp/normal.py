from threading import Event, Thread

default_config={
    'exit':'esc',
    'left':'h',
    'down':'j',
    'up':'k',
    'right':'l',
    'accelerate':'a',
    'deccelerate':'d',
    'scroll':'s',
    'left click':'space',
    'right click':'alt_gr',
    'middle click':'ctrl_r',
    'click and exit':'i',
    'speed':5.0,
    'scroll speed':0.5,
    'accelerate multiplier':4.0,
    'deccelerate multiplier':.25,
    'fps':60
}

class Mode:
    def __init__(self, config: dict, mousemanager: object, displaymanager: object, change_mode: callable):
        self.config = config
        self.mousemanager = mousemanager
        self.name = 'Normal'
        self.change_mode = change_mode

        self.input_dir = [0, 0]
        self.holding_accel = False
        self.holding_deccel = False
        self.holding_scroll = False

        self.main_thread_stopper = Event()
        self.main_thread = Thread(target = self.main_loop)
        self.main_thread.start()
    

    def main_loop(self):
        interval = 1.0/self.config['fps']
        curspeed: float
        while not self.main_thread_stopper.is_set():
            curspeed = ((self.config['accelerate multiplier'] if self.holding_accel else 1) *
                        (self.config['deccelerate multiplier'] if self.holding_deccel else 1))

            if self.holding_scroll:
                curspeed *= self.config['scroll speed']
                self.mousemanager.scroll(self.input_dir[0]*curspeed, -1*self.input_dir[1]*curspeed)
            else:
                curspeed *= self.config['speed']
                self.mousemanager.move(self.input_dir[0]*curspeed, self.input_dir[1]*curspeed)
            
            self.main_thread_stopper.wait(interval)
    

    def stop_thread(self):
        self.main_thread_stopper.set()
        self.main_thread.join()

    
    def take_input(self, inp: str, released: bool, held_keys: set = {}, just_pressed: bool = False):
        # Mode switcher
        if not released and inp in self.config['modes']:
            self.stop_thread()
            self.change_mode(self.config['modes'][inp], inp)
            return False


        # Directions
        if inp == self.config['left']:
            if released:
                if self.config['right'] in held_keys:
                    self.input_dir[0] = 1
                else:
                    self.input_dir[0] = 0
            else:
                self.input_dir[0] = -1
        elif inp == self.config['right']:
            if released:
                if self.config['left'] in held_keys:
                    self.input_dir[0] = -1
                else:
                    self.input_dir[0] = 0
            else:
                self.input_dir[0] = 1
        elif inp == self.config['down']:
            if released:
                if self.config['up'] in held_keys:
                    self.input_dir[1] = -1
                else:
                    self.input_dir[1] = 0
            else:
                self.input_dir[1] = 1
        elif inp == self.config['up']:
            if released:
                if self.config['down'] in held_keys:
                    self.input_dir[1] = 1
                else:
                    self.input_dir[1] = 0
            else:
                self.input_dir[1] = -1

        # Modifiers
        elif inp == self.config['accelerate']:
            if released:
                self.holding_accel = False
            else:
                self.holding_accel = True
        elif inp == self.config['deccelerate']:
            if released:
                self.holding_deccel = False
            else:
                self.holding_deccel = True
        elif inp == self.config['scroll']:
            if released:
                self.holding_scroll = False
            else:
                self.holding_scroll = True

        # Clicks
        elif inp == self.config['left click']:
            if released:
                self.mousemanager.release(0)
            else:
                self.mousemanager.press(0)
        elif inp == self.config['right click']:
            if released:
                self.mousemanager.release(1)
            else:
                self.mousemanager.press(1)
        elif inp == self.config['middle click']:
            if released:
                self.mousemanager.release(2)
            else:
                self.mousemanager.press(2)
        elif not released and inp==self.config['click and exit']:
            self.mousemanager.click(0)
            self.change_mode('')

        # Special
        elif inp == self.config['exit']:
            if not released:
                self.stop_thread()
                self.change_mode('')
            

        return True
