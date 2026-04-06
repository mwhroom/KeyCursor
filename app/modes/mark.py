# *** COMMENTS HERE FOR NOW, DELETED LATER ***

#Alright, so the mark and goto mark things will be separate modes, you can see what a mode looks like in the normal.py in the Modes folder. For this you
# probably don't need a main loop, and thus don't need anything from the threading library, so you can ignore that.

#You will make 2 modes, mark.py and goto_mark.py, each with the class Mode with an init function taking in the config, mousemanager, displaymanager, and
# change_mode parameters. These are all objects you could use, but if you don't use them, put underscore in front of the variable names to show that you aren't using them.
# One that you absolutely will use, is the change_mode callable, that allows you to change the current mode. You can input '' (empty char) to completely exit the program,
# but you will usually input 'normal' to  change to normal mode.

#Each mode also needs its take_input function, which takes in a string for input, a bool telling you if it was released, the set for all held keys, and a just_pressed bool
# which tells you if the inp key was just pressed. In this function, you will process inputs to do whatever you want them to do.
#You will also edit the default config in main.py, adding another entry in the 'mode config' dictionary for 'mark' and 'goto_mark', and create whatever config details you
# need. You would put the name of the detail first, then the inp string you expect after the colon. Or, you could store variables; just anything the user might ever want to
# edit. Don't create an individual key for every possible mark though, make it reasonable.
#For example, you might want to specify the mark storage location using the config_dir global that you can find within the generate_default_config function. To update your
# config.json, delete it and run the program, and the config should be generated.

#The mark.py mode will take in 1 inp string, and assign it to a coordinate. Make sure to make a case for a button (that could be configurable) that would just exit the mode
# and return to normal mode without setting the coordinate. This coordinate is the mouse's current position, and will be stored in a persistent file, such as a json file.
# You can see examples of how to handle a json file with all the config stuff in main.

#The goto_mark.py mode will take in 1 inp string, and attempt to retrieve a coordinate that was set by mark.py based on the inp string provided. If the inp string cannot be
# found in whatever storage system you are using, the immediately exit and return to normal mode. Remember to make a normal mode case for this mode as well.

#However, I took a look at the mark.py, but couldn't seem to get it to work; is it working for you?

#Besides that, I think I just assumed you knew about how mark worked in vim and went with that, because it seems like I still wasn't specific enough about what mark was specifically supposed to do. 

#First of all, it is impossible to interfere with other inputs, because all inputs are routed to whichever mode is currently active, so you don't have to worry about those kinds of mapping issues. 

#Second, it looks like you put in a case for the 'modes' input, when in reality, that is exclusively for the normal mode; unless you add a section for it to the config, it won't appear in the mark's config dictionary. But you shouldn't need this at all because of my third comment:

#Third, the mark mode should minimize the amount of button presses necessary. This means it should have as little stuff going on as possible, so we don't really need a whole section for marking, saving, and deleting. The only overhead you should have is a keybind for exiting the mark mode without marking anything and returning to normal mode, which can be esc, capslock, or whatever. All the mark mode needs to do is take 1 key, not just numbers, any key (this is the inp string I was mentioning in the overview; in the take_input() function, it is the inp argument), read the current cursor position, and update the json with this information (which means either overwrite an existing marked position, or making a new one if it does not exist).

#Everything else seems great, though I wasn't really able to test it, it looks like you are reading from and writing to the json file correctly, and updating your dictionary well. Let me know if you have any questions
# *** COMMENTS HERE FOR NOW, DELETED LATER ***

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