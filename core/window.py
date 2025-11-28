from typing import Tuple, Optional, Sequence
import pyautogui

def _wrect(w) -> Tuple[int, int, int, int]:
    return (w.left, w.top, w.width, w.height)

def detect_game_roi(title_candidates: Optional[Sequence[str]] = None) -> Tuple[int, int, int, int]:
    title_candidates = title_candidates or ("RuneLite", "Old School RuneScape", "OSRS", "OSBuddy")
    try:
        if hasattr(pyautogui, "getWindowsWithTitle"):
            for t in title_candidates:
                ws = pyautogui.getWindowsWithTitle(t)
                if ws:
                    w = ws[0]
                    if w.width >= 800 and w.height >= 600:
                        return _wrect(w)
    except Exception:
        pass
    try:
        if hasattr(pyautogui, "getAllWindows"):
            wins = pyautogui.getAllWindows()
            candidates = []
            for w in wins:
                title = (w.title or "").lower()
                if w.width < 800 or w.height < 600:
                    continue
                if title in ("tk", "python"):
                    continue
                if any(k in title for k in ["runelite", "old school", "osrs", "osbuddy"]):
                    candidates.append(w)
            if candidates:
                w = sorted(candidates, key=lambda ww: ww.width * ww.height, reverse=True)[0]
                return _wrect(w)
            # fallback: largest window meeting size
            large = [w for w in wins if w.width >= 800 and w.height >= 600]
            if large:
                w = sorted(large, key=lambda ww: ww.width * ww.height, reverse=True)[0]
                return _wrect(w)
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
