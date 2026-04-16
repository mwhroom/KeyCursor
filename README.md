# KeyCursor
W.I.P

Full control over your mouse with your keyboard.

Currently supports:
- Windows
- MacOS
- Linux
  - X11 (not tested)
  - Wayland (limited & buggy)

## Features
Different modes to enhance your mouse movement.
Keys specified here are the defaults, freely editable in the config.json file.
- Default mode: Normal
    - Move cursor in direction:
        - H: Left
        - J: Down
        - K: Up
        - L: Right
    - Click mouse buttons:
        - Space: Left Click
        - Right alt: Right Click
        - Right ctrl: Middle Click
    - Hold A to move fast, D to move slow 
    - Hold S to scroll
- G: Grid
    - Using a set of home row keys, specify a point on a grid with a combination of 2 characters.
    - Default set: {A, S, D, F, G, H, J, K, L}
    - First input specifies a point from left to right, second input specifies a point from top to bottom
    - Moves cursor to that point
- B: Bisect
    - Using directional keys, move cursor to a point half way between your current position, and the max possible position in the specified direction.
        - H: Left
        - J: Down
        - K: Up
        - L: Right
    - Max and min possible position update based on direction.
    - Like binary search, enables logarithmic movement of cursor.
- M: Mark
    - Assign the current cursor position to a key
    - Works with any key
- ': Goto Mark
    - Reading the assigned positions from Mark mode, move cursor to specified key's stored cursor position
    - Works with any key used in Mark mode

Easy to make your own modes! Check docs/ (coming soon) for more details.

## Install Requirements
pip install -r requirements.txt

If on Linux, install gtk and also call: pip install pygobject
If on Wayland, install ydotool and also call: pip install python-ydotool
- You'll need the ydotool daemon running in the background for this. (sudo ydotoold)

This was made for Project Launch, from Knight Hacks.
