import time
from typing import List, Optional, Tuple

import cv2
import numpy as np
import pyautogui
from PIL import Image

pyautogui.FAILSAFE = False

def _grab_screen(roi: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
    img = pyautogui.screenshot()
    if roi:
        x, y, w, h = roi
        img = img.crop((x, y, x + w, y + h))
    arr = np.array(img)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    return bgr

class TemplateMatcher:
    def __init__(self, method: int = cv2.TM_CCOEFF_NORMED):
        self.method = method

    def find(self, templates: List[np.ndarray], roi: Optional[Tuple[int, int, int, int]], threshold: float) -> Optional[Tuple[int, int, int, int, float]]:
        screen_bgr = _grab_screen(roi)
        best = None
        for tmpl in templates:
            res = cv2.matchTemplate(screen_bgr, tmpl, self.method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val >= threshold:
                th, tw = tmpl.shape[:2]
                bx = (roi[0] if roi else 0) + max_loc[0]
                by = (roi[1] if roi else 0) + max_loc[1]
                candidate = (bx, by, tw, th, float(max_val))
                if best is None or candidate[4] > best[4]:
                    best = candidate
        return best

def load_templates(paths: List[str]) -> List[np.ndarray]:
    items = []
    for p in paths:
        try:
            img = cv2.imread(p)
            if img is not None:
                items.append(img)
        except Exception:
            pass
    return items

def is_idle(roi: Tuple[int, int, int, int], duration_ms: int, threshold: float) -> bool:
    a = _grab_screen(roi)
    time.sleep(duration_ms / 1000.0)
    b = _grab_screen(roi)
    diff = cv2.absdiff(a, b)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    mean = float(np.mean(gray))
    return mean < threshold

