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
        self.i = 0
        #makes empty dict to store marks in, will be filled with mark_config.json contents
        self.mark_config = {}
        #initializes the current position as non-existent
        self.curPos = None

    #created because its used in both save and delete
    #more condensed, less repetitive
    def load_logic(self, config_dir):
        if os.path.exists(config_dir):
            with open(config_dir, 'r') as file:
                #loads current marks into dict
                self.mark_config = json.load(file)
        else:
            #if file doesn't exist, make it
            with open(config_dir, 'w') as file:
                #makes empty json with formatting
                json.dump({}, file, indent=2)

    def del_position(self, config_dir, inp: int):
        self.load_logic(config_dir)
        if inp in self.mark_config:
            del self.mark_config[inp]
            #replace the space that the deleted mark was in with the next mark
            if self.i > inp:
                self.i-=1
            with open(config_dir, 'w') as file:
                json.dump(self.mark_config, file, indent=2)
        else:
            #in the case that here is no mark. wont go in here if
            #the mark # is found in mark_config[inp] indexes
            print("Mark not found, cannot delete")


    def save_position(self, curPos, config_dir):

        self.load_logic(config_dir)
        if self.i > 9:
            #overwrites 0 because trying to get saves mapped 0-9
            #no keys because that would be difficult considering this is for keyboard
            self.i = 0
        self.mark_config[self.i] = curPos
        #mapping 0-9
        self.i+=1
        #opens file
        with open(config_dir, 'w') as file:
            #writes to file
            json.dump(self.mark_config, file, indent=2)

    def take_input(self, inp: str, released: bool, held_keys: set = {}, just_pressed: bool = False):
        print("'Z' to mark, 'A' to save, 'X' to Delete")
        #if there is a mode in self.config that corresponds to the inp then switch
        if inp in self.config['modes'][inp]:
            # Can bring it back to normal mode
            # switches to whatever mode user wants to go to
            self.change_mode(self.config['modes'][inp])
        
        #if key mapped to delete is pressed
        if inp == self.config['delete']:
            print("Enter number to mark to delete")

        if inp == self.config['mark']:
            self.curPos = self.mousemanager.get_pos()

        #once a is reached, save position
        if inp == self.config['save']:
            #self object needs to call function to save position in dict
            #ensures theres a position to save
            if self.curPos is not None:
                self.save_position(self.curPos, config_dir)
            else:
                print("No position to save. Press mark key to set a position first.")