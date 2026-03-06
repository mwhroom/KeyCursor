from pynput.keyboard import Listener, Key, KeyCode

input_func: callable
held_keys = set()


def init(suppression: bool):
    with Listener(on_press=press, on_release=release, suppress=suppression) as listener:
        listener.join()


def set_reciever(inp_func: callable):
    global input_func
    input_func = inp_func


def press(key):
    new_input(key, False)


def release(key):
    new_input(key, True)


def new_input(key, released):
    global input_func, held_keys
    inp: str

    if type(key)==Key:
        inp = str(key)[4:]
    elif type(key)==KeyCode:
        inp = key.char
    
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
    