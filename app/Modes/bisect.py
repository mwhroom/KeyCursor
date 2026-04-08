import cairo
class Mode:
    def __init__(self, config: dict, mousemanager: object, displaymanager: object, change_mode: callable):
        self.config = config
        self.mousemanager = mousemanager
        self.displaymanager = displaymanager
        self.name = 'Bisect'
        self.change_mode = change_mode
        
        self.mins = [0, 0]
        self.maxs = [self.displaymanager.screen_width, self.displaymanager.screen_height]
        self.draw_grid()


    def take_input(self, inp: str, released: bool, held_keys: set = {}, just_pressed: bool = False):
        if not released:
            if inp == self.config['exit']:
                self.change_mode('normal')
                return

            if inp == self.config['left']:
                self.maxs[0] = self.mousemanager.get_pos()[0]
            elif inp == self.config['down']:
                self.mins[1] = self.mousemanager.get_pos()[1]
            elif inp == self.config['up']:
                self.maxs[1] = self.mousemanager.get_pos()[1]
            elif inp == self.config['right']:
                self.mins[0] = self.mousemanager.get_pos()[0]
            else:
                return
            self.mousemanager.set_pos(((self.mins[0]+self.maxs[0])//2, 
                                        (self.mins[1]+self.maxs[1])//2))
            self.draw_grid()
                    

    def draw_grid(self):
        # Setup surface
        surface = self.displaymanager.start_draw()
        ctx = cairo.Context(surface)
        ctx.set_antialias(cairo.ANTIALIAS_NONE)

        # Set line properties
        ctx.set_source_rgb(self.config['line color'][0]/255, 
                           self.config['line color'][1]/255, 
                           self.config['line color'][2]/255)
        ctx.set_line_self.width(self.config['line width'])

        # Draw Borders
        ctx.move_to(self.mins[0], self.mins[1])
        ctx.line_to(self.maxs[0], self.mins[1])
        ctx.line_to(self.maxs[0], self.maxs[1])
        ctx.line_to(self.mins[0], self.maxs[1])
        ctx.close_path()
        ctx.stroke()

        # Draw Bisect
        mouse_pos = self.mousemanager.get_pos()
        ctx.move_to(mouse_pos[0], self.mins[1])
        ctx.line_to(mouse_pos[0], self.maxs[1])
        ctx.stroke()
        ctx.move_to(self.mins[0],  mouse_pos[1])
        ctx.line_to(self.maxs[0], mouse_pos[1])
        ctx.stroke()
