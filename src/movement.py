import time
import math
import random
from typing import Tuple, List

import numpy as np
import pyautogui

pyautogui.FAILSAFE = False

def _quad_bezier(p0: Tuple[int, int], p1: Tuple[int, int], p2: Tuple[int, int], t: float) -> Tuple[float, float]:
    u = 1.0 - t
    x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
    y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
    return x, y

def _random_control_point(p0: Tuple[int, int], p2: Tuple[int, int], curvature: float, jitter: float) -> Tuple[int, int]:
    mx = (p0[0] + p2[0]) / 2.0
    my = (p0[1] + p2[1]) / 2.0
    dx = p2[0] - p0[0]
    dy = p2[1] - p0[1]
    length = math.hypot(dx, dy) + 1e-6
    nx = -dy / length
    ny = dx / length
    offset = curvature * length
    jx = np.random.normal(0, jitter)
    jy = np.random.normal(0, jitter)
    cx = mx + nx * offset + jx
    cy = my + ny * offset + jy
    return int(cx), int(cy)

def _generate_path(start: Tuple[int, int], end: Tuple[int, int], profile: dict) -> List[Tuple[int, int]]:
    curvature = float(profile.get("curvature", 0.15))
    jitter = float(profile.get("path_jitter", 2.5))
    p1 = _random_control_point(start, end, curvature, jitter)
    dist = math.hypot(end[0] - start[0], end[1] - start[1])
    steps_min = int(profile.get("steps_min", 35))
    steps_max = int(profile.get("steps_max", 95))
    steps = max(steps_min, min(steps_max, int(dist / profile.get("pixels_per_step", 6))))
    ts = np.linspace(0.0, 1.0, steps)
    pts = []
    for t in ts:
        x, y = _quad_bezier(start, p1, end, t)
        x += np.random.normal(0, jitter * 0.4)
        y += np.random.normal(0, jitter * 0.4)
        pts.append((int(x), int(y)))
    return pts

def move_mouse_curved(to: Tuple[int, int], profile: dict, click: bool = False, button: str = "left") -> None:
    start = pyautogui.position()
    path = _generate_path((start.x, start.y), to, profile)
    base_delay = float(profile.get("step_delay_ms", 6)) / 1000.0
    delay_sigma = float(profile.get("step_delay_sigma", 0.45))
    for x, y in path:
        d = max(0.0, np.random.normal(base_delay, base_delay * delay_sigma))
        pyautogui.moveTo(x, y, duration=0)
        time.sleep(d)
    if click:
        click_delay = float(profile.get("click_delay_ms", 35)) / 1000.0
        time.sleep(max(0.0, np.random.normal(click_delay, click_delay * 0.25)))
        pyautogui.click(to[0], to[1], button=button)

def random_point_in_bbox(bbox: Tuple[int, int, int, int], offset_pixels: int, sigma_ratio: float = 0.45) -> Tuple[int, int]:
    x, y, w, h = bbox
    cx = x + w // 2
    cy = y + h // 2
    sigma = max(1.0, offset_pixels * sigma_ratio)
    rx = int(np.random.normal(cx, sigma))
    ry = int(np.random.normal(cy, sigma))
    rx = max(x, min(x + w - 1, rx))
    ry = max(y, min(y + h - 1, ry))
    return rx, ry

