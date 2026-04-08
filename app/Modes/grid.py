import cairo
class Mode:
    def __init__(self, config: dict, mousemanager: object, displaymanager: object, change_mode: callable):
        self.config = config
        self.mousemanager = mousemanager
        self.displaymanager = displaymanager
        self.name = 'Grid'
        self.change_mode = change_mode

        self.current_input = ''
        self.made_first_input = False

        self.width = displaymanager.screen_width
        self.height = displaymanager.screen_height


    def take_input(self, inp: str, released: bool, held_keys: set = {}, just_pressed: bool = False):
        if not released:
            if inp == 'esc':
                if self.made_first_input:
                    self.made_first_input = False
                    self.current_input = ''
                    self.draw_grid()
                else:
                    self.change_mode('normal')
            elif inp in self.config['keys']:
                if self.made_first_input:
                    self.goto_input(inp)
                else:
                    self.made_first_input = True
                    self.current_input = inp
                    self.draw_grid()
            else:
                print('key not found in', self.config['keys'])

                
    def goto_pos(self, second_input: str):
        len_keys = len(self.config['keys'])
        width = self.displaymanager.screen_width
        height = self.displaymanager.screen_height
        step_row = width//len_keys
        step_col = height//len_keys

        self.mousemanager.set_pos(self.config['keys'].find(self.current_input) * step_col, 
                                  self.config['keys'].find(second_input)       * step_row)


    def draw_grid(self):
        len_keys = len(self.config['keys'])
        step_row = self.height//len_keys
        step_col = self.width//len_keys

        # Setup surface
        surface = self.displaymanager.start_draw()
        ctx = cairo.Context(surface)
        ctx.set_antialias(cairo.ANTIALIAS_NONE)

        # Fill background
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        ctx.fill()
        
        # Draw vertical lines
        ctx.set_source_rgb(self.config['line color'][0]/255, 
                           self.config['line color'][1]/255, 
                           self.config['line color'][2]/255)
        ctx.set_line_self.width(self.config['line width'])
        for col in range(len_keys):
            ctx.move_to(col*step_col, 0)
            ctx.line_to(col*step_col, self.height)
            ctx.stroke()
        
        # Draw highlighted column if exists
        if self.current_input != '':
            ctx.set_source_rgb(self.config['highlight line color'][0]/255, 
                               self.config['highlight line color'][1]/255, 
                               self.config['highlight line color'][2]/255)
            ctx.set_line_self.width(self.config['highlight line width'])

            highlight_pos = self.config['keys'].find(self.current_input)
            ctx.move_to(highlight_pos*step_col, 0)
            ctx.line_to(highlight_pos*step_col, self.height)
            ctx.stroke()
            ctx.move_to((highlight_pos+1)*step_col, 0)
            ctx.line_to((highlight_pos+1)*step_col, self.height)
            ctx.stroke()

        # Set text properties
        ctx.set_line_self.width(self.config['line width'])
        ctx.set_font_size(self.config['font size'])
        ctx.select_font_face(self.config['font'], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

        for row in range(len_keys):
            # Draw horizontal line
            ctx.move_to(0, row*step_row)
            ctx.line_to(self.width, row*step_row)
            ctx.set_source_rgb(self.config['line color'][0]/255, 
                               self.config['line color'][1]/255, 
                               self.config['line color'][2]/255)
            ctx.stroke()

            # Prepare to draw text
            ctx.set_source_rgb(self.config['font color'][0]/255, 
                               self.config['font color'][1]/255, 
                               self.config['font color'][2]/255)
            for col in range(len_keys):
                # Print text in center of grid box
                text = (self.config['keys'][col] if not self.made_first_input else '') + self.config['keys'][row]
                text_size = ctx.text_extents(text)

                ctx.move_to(col*step_col, row*step_row)
                ctx.rel_move_to((step_col-text_size.width)//2, (step_row+text_size.height)//2)

                ctx.show_text(text)
        surface.flush()
        
        self.displaymanager.stop_draw()
