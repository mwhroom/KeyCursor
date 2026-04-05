import inputmanager

from importlib import import_module
from os import path
import json
import sys

config = {}
mousemanager = None
displaymanager = None
mode = None

app_path = path.dirname(path.abspath(__file__))
config_dir = path.join(path.join(app_path, '..'), 'config.json')

# Attempts to create a new default config.json file.
def generate_default_config():
    global config_dir
    default_config = {
        'display system':'windows', 
        'homerow':'asdfghjkl', 
        'modes':{
            'g':'grid',
            'f':'next_color',
            'm':'mark',
            '`':'goto_mark',
        }, 
        'mode config':{
            'normal':{
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
                'speed':5.0,
                'scroll speed':0.5,
                'accelerate multiplier':4.0,
                'deccelerate multiplier':.25,
                'fps':60
            }
        }
    }

    try:
        with open(config_dir, 'w') as file:
            json.dump(default_config, file, indent=2)
    except:
        print("Couldn't create config.json.")
        return False

    global config
    config = default_config
    return True


# Attempts to load config.json
# Returns True if successful, False if not.
def load_config():
    global config, config_dir
    print('loading config...')
    try:
        with open(config_dir, 'r') as file:
            config = json.load(file)
        
        for x in ['display system', 'mode config', 'homerow', 'modes']:
            if x not in config:
                print(f'"{x}" is not defined in config.')
                raise AttributeError

        if config['display system'] not in {'windows', 'x11', 'wayland'}:
            print('Incorrect display system: Make sure "display system" is set to "windows" or "x11" or "wayland"')
            raise AttributeError

        if 'normal' not in config['mode config']:
            print('"normal" mode config not defined in "mode config" in config.json')

        for x in ['left', 'down', 'up', 'right', 'accelerate', 'deccelerate', 'scroll', 
                  'left click', 'right click', 'middle click',
                  'speed', 'scroll speed', 'accelerate multiplier', 'deccelerate multiplier', 'fps']:
            if x not in config['mode config']['normal']:
                print(f'"{x}" is not defined in "normal" in "mode config".')
                raise AttributeError
        

    except FileNotFoundError:
        print('Config json not found. Generating new config...')
        return generate_default_config()
    except AttributeError:
        print('Config file is incorrect.')
        return False
    except json.JSONDecodeError:
        print('Config json could not be decoded.')
        return False
    except:
        print('Something went wrong when loading the config.json file.')
        return False
    return True


def change_mode(m: str):
    global mode

    if m=='':
        sys.exit()

    module = import_module('Modes.'+m)
    mode = module.Mode(config['mode config'][m], mousemanager, displaymanager, change_mode)
    inputmanager.set_reciever(mode.take_input)


if __name__ == "__main__":
    if not load_config():
        sys.exit()
    config['mode config']['normal']['modes'] = config['modes']

    match config['display system']:
        case 'windows':
            mousemanager = import_module('MouseManagers.pynput_mouse').Manager()
            #displaymanager = import_module('DisplayManagers.win')
        case 'x11':
            mousemanager = import_module('MouseManagers.pynput_mouse').Manager()
            displaymanager = import_module('DisplayManagers.x11')
        case 'wayland':
            mousemanager = None
            displaymanager = import_module('DisplayManagers.wayland')

    change_mode('normal')
    inputmanager.init(config['display system']!='wayland')