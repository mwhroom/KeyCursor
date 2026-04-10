import inputmanager
from importlib import import_module
import os
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
        'modes':{
            'g':'grid',
            'b':'bisect',
            'm':'mark',
            "'":'goto_mark',
        }, 
        'mode config':dict()
    }

    default_config['mode config']['normal'] = import_module('Modes.normal').default_config

    for _key, m in default_config['modes'].items():
        mode = import_module('Modes.'+m)
        default_config['mode config'][m] = mode.default_config

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
        
        for x in ['mode config', 'modes']:
            if x not in config:
                print(f'"{x}" is not defined in config.')
                raise AttributeError

        if 'normal' not in config['mode config']:
            print('"normal" mode config not defined in "mode config" in config.json')
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


def change_mode(m: str, key_used: str=''):
    global mode, displaymanager, mousemanager
    if m=='':
        print('exiting.')
        del displaymanager, mousemanager
        sys.exit(0)

    displaymanager.clear_screen()

    try:
        module = import_module('Modes.'+m)
    except:
        print("Couldn't load mode", m)
        return

    del mode

    for key in module.default_config.keys():
        if key not in config['mode config'][m]:
            config['mode config'][m][key] = module.default_config[key]
    config['mode config'][m]['self'] = key_used

    mode = module.Mode(config['mode config'][m], mousemanager, displaymanager, change_mode)
    inputmanager.set_reciever(mode.take_input)


if __name__ == "__main__":
    if not load_config():
        sys.exit(1)
    config['mode config']['normal']['modes'] = config['modes']

    iswayland = False
    match sys.platform:
        case 'win32':
            mousemanager = import_module('MouseManagers.pynput_mouse').Manager()
            displaymanager = import_module('DisplayManagers.win').Manager()
        case 'linux':
            session = os.getenv('XDG_SESSION_TYPE')
            if session=='wayland':
                iswayland = True
                mousemanager = import_module('MouseManagers.pynput_mouse').Manager()
                displaymanager = import_module('DisplayManagers.wayland').Manager()
            elif session=='x11':
                mousemanager = import_module('MouseManagers.pynput_mouse').Manager()
                displaymanager = import_module('DisplayManagers.x11').Manager()
            else:
                print("Unknown session type.")
                sys.exit(1)
        case 'darwin':
            mousemanager = import_module('MouseManagers.pynput_mouse').Manager()
            displaymanager = import_module('DisplayManagers.macos').Manager()

    change_mode('normal')
    inputmanager.init(not iswayland)