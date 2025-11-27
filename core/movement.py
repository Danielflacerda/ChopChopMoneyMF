import time
import math
from typing import Tuple, List, Dict, Callable

import numpy as np
import pyautogui

pyautogui.FAILSAFE = False

def _q_bezier(p0: Tuple[int, int], p1: Tuple[int, int], p2: Tuple[int, int], t: float) -> Tuple[float, float]:
    u = 1.0 - t
    x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
    y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
    return x, y

def _random_control(p0: Tuple[int, int], p2: Tuple[int, int], deviation: float, variance: float) -> Tuple[int, int]:
    mx = (p0[0] + p2[0]) / 2.0
    my = (p0[1] + p2[1]) / 2.0
    dx = p2[0] - p0[0]
    dy = p2[1] - p0[1]
    length = math.hypot(dx, dy) + 1e-6
    nx = -dy / length
    ny = dx / length
    offset = deviation
    jx = np.random.normal(0, deviation * variance)
    jy = np.random.normal(0, deviation * variance)
    cx = mx + nx * offset + jx
    cy = my + ny * offset + jy
    return int(cx), int(cy)

def move_to_bezier(end_x: int, end_y: int, deviation: float = 35.0, control_variance: float = 0.4, duration_mean: float = 0.6, duration_std: float = 0.18, click: bool = False, button: str = "left") -> None:
    start = pyautogui.position()
    p0 = (start.x, start.y)
    p2 = (end_x, end_y)
    p1 = _random_control(p0, p2, deviation, control_variance)
    dist = math.hypot(p2[0] - p0[0], p2[1] - p0[1])
    steps = max(24, min(120, int(dist / 6)))
    duration = max(0.02, np.random.normal(duration_mean, duration_mean * duration_std))
    step_delay = duration / steps
    ts = np.linspace(0.0, 1.0, steps)
    for t in ts:
        x, y = _q_bezier(p0, p1, p2, float(t))
        x += np.random.normal(0, deviation * 0.12)
        y += np.random.normal(0, deviation * 0.12)
        pyautogui.moveTo(int(x), int(y), duration=0)
        time.sleep(step_delay)
    if click:
        time.sleep(max(0.0, np.random.normal(0.04, 0.01)))
        pyautogui.click(end_x, end_y, button=button)

class MovementEngine:
    def __init__(self):
        self._profiles: Dict[str, Callable[..., None]] = {
            "natural_curved": move_to_bezier
        }

    def move(self, profile: str, x: int, y: int, params: Dict, click: bool = False, button: str = "left") -> None:
        fn = self._profiles.get(profile, move_to_bezier)
        fn(x, y, params.get("bezier_deviation_pixels", 35), params.get("bezier_control_variance", 0.4), params.get("move_duration_mean", 0.6), params.get("move_duration_std", 0.18), click=click, button=button)

def human_click(x: int, y: int, profile: str, params: Dict) -> None:
    move_to_bezier(x, y, params.get("bezier_deviation_pixels", 35), params.get("bezier_control_variance", 0.4), params.get("move_duration_mean", 0.6), params.get("move_duration_std", 0.18), click=True)

