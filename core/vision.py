from typing import List, Optional, Tuple

import cv2
import numpy as np
import pyautogui
import glob as pyglob

pyautogui.FAILSAFE = False

def _grab_screen(roi: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
    img = pyautogui.screenshot()
    if roi:
        x, y, w, h = roi
        img = img.crop((x, y, x + w, y + h))
    arr = np.array(img)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

class TemplateMatcher:
    def __init__(self, method: int = cv2.TM_CCOEFF_NORMED):
        self.method = method

    def find(self, templates: List[np.ndarray], roi: Optional[Tuple[int, int, int, int]], threshold: float, scales: Optional[List[float]] = None) -> Optional[Tuple[int, int, int, int, float]]:
        screen_bgr = _grab_screen(roi)
        best = None
        scales = scales or [1.0]
        for tmpl in templates:
            for s in scales:
                if s != 1.0:
                    th = int(tmpl.shape[0] * s)
                    tw = int(tmpl.shape[1] * s)
                    if th < 10 or tw < 10:
                        continue
                    tscaled = cv2.resize(tmpl, (tw, th))
                else:
                    tscaled = tmpl
                res = cv2.matchTemplate(screen_bgr, tscaled, self.method)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                if max_val >= threshold:
                    th, tw = tscaled.shape[:2]
                    bx = (roi[0] if roi else 0) + max_loc[0]
                    by = (roi[1] if roi else 0) + max_loc[1]
                    candidate = (bx, by, tw, th, float(max_val))
                    if best is None or candidate[4] > best[4]:
                        best = candidate
        return best

def load_templates(paths_or_globs: List[str]) -> List[np.ndarray]:
    items: List[np.ndarray] = []
    for p in paths_or_globs:
        expanded = list(pyglob.glob(p)) if any(ch in p for ch in ["*", "?", "["]) else [p]
        for path in expanded:
            img = cv2.imread(path)
            if img is not None:
                items.append(img)
    return items

def find_color_bboxes(hsv_ranges: List[Tuple[List[int], List[int]]], roi: Optional[Tuple[int, int, int, int]], min_area: int) -> List[Tuple[int, int, int, int, int]]:
    bgr = _grab_screen(roi)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask_total = None
    for low, high in hsv_ranges:
        ml = np.array(low, dtype=np.uint8)
        mh = np.array(high, dtype=np.uint8)
        m = cv2.inRange(hsv, ml, mh)
        mask_total = m if mask_total is None else cv2.bitwise_or(mask_total, m)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask_total, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    res: List[Tuple[int, int, int, int, int]] = []
    offx = roi[0] if roi else 0
    offy = roi[1] if roi else 0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        if area >= min_area:
            res.append((offx + x, offy + y, w, h, area))
    return res
