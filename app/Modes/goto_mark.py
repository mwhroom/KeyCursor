import json
import os
from os import path

default_config={
    'normal':'esc',
    'exit':''
}

app_path = path.dirname(path.abspath(__file__))
config_dir = path.join(path.join(app_path, '..'), 'mark_config.json')

class Mode:
    def __init__(self, config, mousemanager, _displaymanager, change_mode):
        self.config = config
        self.name = 'goto_mark'
        self.mousemanager = mousemanager
        self.change_mode = change_mode

    def take_input(self, inp: str, released: bool, held_keys: set = {}, just_pressed: bool = False):
        if released:
            return
        #check to see if user wants to go back to normal mode. 'esc' key. if exit ''
        if inp == self.config['normal']:
            self.change_mode('normal')
            return
        elif inp == self.config['exit']:
            self.change_mode('')
            return


        else: #go to marked position
            try:
                with open(config_dir, 'r') as file:
                    mark_config = json.load(file)
                    if inp in mark_config:
                        pos = mark_config[inp]
                        print(f"Moving cursor to {pos}")
                        #corrected. now sets position rather than move
                        self.mousemanager.set_pos(pos[0], pos[1])

                    else:
                        #if no mark found, do nothing and return to normal mode
                        print(f"No mark found for {inp}")
                        return
            except:
                #no marks set yet, no positions to go to
                print("No marks have been set yet. Press m to go into mark mode.")
                return
            #needs to return to normal mode at the end after going to the mark
            self.change_mode('normal')


