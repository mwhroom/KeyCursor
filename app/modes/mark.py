import json
import os
from os import path

#stores absolute path to app folder
app_path = path.dirname(path.abspath(__file__))
#outside of app folder stores mark_config.json. goes to parent to look for it
config_dir = path.join(path.join(app_path, '..'), 'mark_config.json')

class Mode:
    def __init__(self, config, mousemanager, _displaymanager, change_mode):
        self.config = config
        self.name = 'mark'
        self.mousemanager = mousemanager
        self.change_mode = change_mode
        #makes empty dict to store marks in, will be filled with mark_config.json contents
        #initializes the current position as non-existent
        curPos = None

    def take_input(self, inp: str, released: bool, held_keys: set = {}, just_pressed: bool = False):
        #if m released, do nothing. only mark on press not release
        if released:
            return
        
        #check to see if user wants to go back to normal mode. 'esc' key. if exit ''
        if inp == self.config['normal']:
            self.change_mode('normal')
        elif inp == self.config['exit']:
            self.change_mode('')
            
        else:
        #marks position
            curPos = self.mousemanager.get_pos()
            print(f"Marking position {curPos}")
            #initializes this dict empty incase try fails and the if/else does not execute
            mark_config = {}
            try:
                #checks if path exists
                if os.path.exists(config_dir):
                    with open(config_dir, 'r') as file:
                        #loads current marks into dict
                        # overwrites empty initialized one aswell
                        mark_config = json.load(file)
                #if file doesnt exist yet, makes an empty one
                else:
                    #initializes empty mark_config file
                    mark_config = {}
            except:
                print('Could not write to mark_config.json')
            #stored in mark_config dict
            mark_config[inp] = curPos
            
            #now that either open file is known to exist or empty initialized, write to it
            with open(config_dir, 'w') as file:
                json.dump(mark_config, file, indent=2)

            #automatically changes back to normal mode at the end
            self.change_mode('normal')