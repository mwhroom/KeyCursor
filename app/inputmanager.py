import os

iswayland = False
stop = False

match os.getenv('XDG_SESSION_TYPE', 'unknown'):
    case 'wayland':
        iswayland = True
        os.environ['PYNPUT_BACKEND_KEYBOARD'] = 'uinput'
        os.environ['PYNPUT_BACKEND_MOUSE'] = 'dummy'

from pynput.keyboard import Listener, Key, KeyCode


input_func: callable
held_keys = set()
listener_thread = None

def init():
    global iswayland, listener_thread
    if iswayland:
        import glob
        p = glob.glob('/dev/input/by-id/*-kbd') + glob.glob('/dev/input/by-id/*-event-kbd')
        i = p if p else glob.glob('/dev/input/by-path/*-kbd') + glob.glob('/dev/input/by-path/*-event-kbd')
        listener_thread = Listener(on_press=press, on_release=release, 
                      uinput_device_paths=(i if i else glob.glob('/dev/input/event*')),
                      suppress=True)
    else:
        listener_thread = Listener(on_press=press, on_release=release, suppress=True)
    listener_thread.start()


def set_reciever(inp_func: callable):
    global input_func
    input_func = inp_func


def press(key):
    return new_input(key, False)


def release(key):
    return new_input(key, True)


def new_input(key, released):
    global stop
    if stop:
        return False
    global input_func, held_keys
    inp = ''

    if type(key)==Key:
        inp = str(key)[4:]
    elif type(key)==KeyCode:
        inp = key.char
    
    if inp!='':
        if released:
            if inp in held_keys:
                held_keys.remove(inp)
            input_func(inp, True, held_keys)
        else:
            if inp in held_keys:
                input_func(inp, False, held_keys, True)
            else:
                input_func(inp, False, held_keys)
            held_keys.add(inp)

    return True
    
