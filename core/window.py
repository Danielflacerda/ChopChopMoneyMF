from typing import Tuple, Optional
import pyautogui

def detect_game_roi(title_candidates = ("RuneLite", "Old School RuneScape", "OSRS")) -> Tuple[int, int, int, int]:
    try:
        if hasattr(pyautogui, "getActiveWindow"):
            w = pyautogui.getActiveWindow()
            if w:
                return (w.left, w.top, w.width, w.height)
    except Exception:
        pass
    try:
        if hasattr(pyautogui, "getWindowsWithTitle"):
            for t in title_candidates:
                ws = pyautogui.getWindowsWithTitle(t)
                if ws:
                    w = ws[0]
                    return (w.left, w.top, w.width, w.height)
    except Exception:
        pass
    sz = pyautogui.size()
    return (0, 0, sz.width, sz.height)

def to_abs_rect(win_roi: Tuple[int, int, int, int], rel: Tuple[float, float, float, float]) -> Tuple[int, int, int, int]:
    x, y, w, h = win_roi
    rx, ry, rw, rh = rel
    ax = x + int(rx * w)
    ay = y + int(ry * h)
    aw = int(rw * w)
    ah = int(rh * h)
    return (ax, ay, aw, ah)

def to_abs_point(win_roi: Tuple[int, int, int, int], rel: Tuple[float, float]) -> Tuple[int, int]:
    x, y, w, h = win_roi
    rx, ry = rel
    return (x + int(rx * w), y + int(ry * h))

