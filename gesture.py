import math

THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

# MCP (knuckle) bases to compare finger extension
INDEX_MCP = 5
MIDDLE_MCP = 9
RING_MCP = 13
PINKY_MCP = 17
THUMB_IP = 3


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _finger_up(tip, mcp):
    return tip[1] < mcp[1]  # tip higher on screen = finger extended


def detect_gesture(lm):
    """
    lm: list of 21 (x, y) tuples from HandTracker.

    Returns one of:
        'move'       - index finger pointing (cursor movement)
        'click'      - pinch: thumb tip close to index tip
        'next_slide' - swipe right gesture (index + middle pointing right)
        'prev_slide' - swipe left (pinky + ring up, index down)
        'scroll_up'  - all fingers up (open palm)
        'scroll_down'- fist (all fingers down)
        'idle'       - unrecognised pose
    """
    if lm is None:
        return 'idle'

    index_up  = _finger_up(lm[INDEX_TIP],  lm[INDEX_MCP])
    middle_up = _finger_up(lm[MIDDLE_TIP], lm[MIDDLE_MCP])
    ring_up   = _finger_up(lm[RING_TIP],   lm[RING_MCP])
    pinky_up  = _finger_up(lm[PINKY_TIP],  lm[PINKY_MCP])

    pinch_dist = _dist(lm[THUMB_TIP], lm[INDEX_TIP])

    # Open palm → scroll up
    if index_up and middle_up and ring_up and pinky_up:
        return 'scroll_up'

    # Fist (all down) → scroll down / drag
    if not index_up and not middle_up and not ring_up and not pinky_up:
        return 'scroll_down'

    # Pinch → click
    if pinch_dist < 40:
        return 'click'

    # Only index up → move cursor
    if index_up and not middle_up and not ring_up:
        return 'move'

    # Index + middle up → next slide (peace sign)
    if index_up and middle_up and not ring_up and not pinky_up:
        return 'next_slide'

    # Ring + pinky up → prev slide
    if not index_up and not middle_up and ring_up and pinky_up:
        return 'prev_slide'

    return 'idle'
