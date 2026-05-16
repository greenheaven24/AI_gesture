import pyautogui
import time

pyautogui.FAILSAFE = True   # move mouse to top-left corner to abort
pyautogui.PAUSE = 0         # no built-in delay between calls


class CursorController:
    def __init__(self, cam_w, cam_h, screen_w, screen_h, smoothing=5, margin_x=0.2, margin_y=0.3):
        self.cam_w = cam_w
        self.cam_h = cam_h
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.smoothing = smoothing
        self.margin_x = margin_x
        self.margin_y = margin_y

        self._prev_x = screen_w // 2
        self._prev_y = screen_h // 2
        self._click_cooldown = 0
        self._slide_cooldown = 0

    def _smooth(self, raw, prev):
        return prev + (raw - prev) / self.smoothing

    def move(self, tip_x, tip_y):
        sx = (tip_x / self.cam_w - self.margin_x) / (1 - 2 * self.margin_x) * self.screen_w
        sy = (tip_y / self.cam_h - self.margin_y) / (1 - 2 * self.margin_y) * self.screen_h
        sx = int(max(0, min(self.screen_w, sx)))
        sy = int(max(0, min(self.screen_h, sy)))

        sx = self._smooth(sx, self._prev_x)
        sy = self._smooth(sy, self._prev_y)

        self._prev_x = sx
        self._prev_y = sy
        pyautogui.moveTo(sx, sy, duration=0)

    def click(self):
        now = time.time()
        if now - self._click_cooldown > 0.6:
            pyautogui.click()
            self._click_cooldown = now

    def next_slide(self):
        now = time.time()
        if now - self._slide_cooldown > 1.0:
            pyautogui.press('right')
            self._slide_cooldown = now

    def prev_slide(self):
        now = time.time()
        if now - self._slide_cooldown > 1.0:
            pyautogui.press('left')
            self._slide_cooldown = now

    def scroll_up(self):
        pyautogui.scroll(3)

    def scroll_down(self):
        pyautogui.scroll(-3)
