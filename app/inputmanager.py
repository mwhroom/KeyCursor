# Key Cursor input management
# Last edited: March 4, 2026

#======== TO INSTALL KEYBOARD MODULE: ========
#         python3 -m pip install pynput

# Bindings:
# H = left, L = right, K = up, J = down
# A = accelerate, D = decelerate, S = scroll mode toggle

from pynput.keyboard import Key, Listener

x = 0
y = 0
scroll_y = 0

speed = 1
MIN_SPEED = 1
MAX_SPEED = 5

is_scrolling = False
keys_held = set()

# Screen-style coordinates:
# +X moves right, -X moves left
# +Y moves down, -Y moves up

# Speed changes based on acceleration.
# Greater speed = larger X and Y displacement.
# Less speed = smaller X and Y displacement.

def move_right() -> None:
    """Move cursor right by the current speed step."""
    global x
    # Increase horizontal position.
    x += speed


def move_left() -> None:
    """Move cursor left by the current speed step."""
    global x
    # Decrease horizontal position.
    x -= speed


def move_down() -> None:
    """Move cursor down by the current speed step."""
    global y
    # Increase vertical position (screen coordinates).
    y += speed


def move_up() -> None:
    """Move cursor up by the current speed step."""
    global y
    # Decrease vertical position (screen coordinates).
    y -= speed


def scroll_down() -> None:
    """Scroll downward by the current speed step."""
    global scroll_y
    # Positive scroll accumulator means scroll down.
    scroll_y += speed


def scroll_up() -> None:
    """Scroll upward by the current speed step."""
    global scroll_y
    # Negative scroll accumulator means scroll up.
    scroll_y -= speed


def decel() -> None:
    """Decrease movement speed, but never below MIN_SPEED."""
    global speed
    # Lower speed by 1 and clamp to minimum.
    speed = max(MIN_SPEED, speed - 1)


def accel() -> None:
    """Increase movement speed, but never above MAX_SPEED."""
    global speed
    # Raise speed by 1 and clamp to maximum.
    speed = min(MAX_SPEED, speed + 1)


def toggle_scroll() -> None:
    """Switch between movement mode and scroll mode."""
    global is_scrolling
    # Flip mode flag: False->True or True->False.
    is_scrolling = not is_scrolling



# For output and state testing purposes only. Will be commented out.
# Will be kept to use for testing if necessary.
# def print_state() -> None:
#    mode = "SCROLL" if is_scrolling else "MOVE"
#    print(f"mode={mode} x={x} y={y} scroll_y={scroll_y} speed={speed}")


movement = {
    "RIGHT": move_right,
    "LEFT": move_left,
    "UP": move_up,
    "DOWN": move_down,
    "SCROLL_UP": scroll_up,
    "SCROLL_DOWN": scroll_down,
    "DECEL": decel,
    "ACCEL": accel,
    "SCROLL_TOGGLE": toggle_scroll,
}


def on_press(key) -> None:
    try:
        pressed = key.char.lower()
    except AttributeError:
        return

    if pressed in keys_held:
        return
    keys_held.add(pressed)

    if pressed == "h":
        movement["LEFT"]()
    elif pressed == "l":
        movement["RIGHT"]()
    elif pressed == "k":
        if is_scrolling:
            movement["SCROLL_UP"]()
        else:
            movement["UP"]()
    elif pressed == "j":
        if is_scrolling:
            movement["SCROLL_DOWN"]()
        else:
            movement["DOWN"]()
    elif pressed == "a":
        movement["ACCEL"]()
    elif pressed == "d":
        movement["DECEL"]()
    elif pressed == "s":
        movement["SCROLL_TOGGLE"]()

# Used for testing.
    # print_state()


def on_release(key):
    if key == Key.esc:
        return False

    try:
        keys_held.discard(key.char.lower())
    except AttributeError:
        pass


if __name__ == "__main__":
    print("Listening... press ESC to exit.")
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
