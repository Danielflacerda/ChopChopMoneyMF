import random
import numpy as np
from typing import Dict, Tuple
import pyautogui

from core.movement import move_to_bezier

def occasional_afk(max_seconds: int) -> None:
    import time
    d = random.randint(1, max_seconds)
    time.sleep(d)

def check_skills_tab(chance: float, params: Dict) -> None:
    if random.uniform(0, 1) < chance:
        pos = pyautogui.position()
        move_to_bezier(pos.x + int(np.random.normal(120, 30)), pos.y + int(np.random.normal(-40, 20)), params.get("bezier_deviation_pixels", 35), params.get("bezier_control_variance", 0.4), params.get("move_duration_mean", 0.6), params.get("move_duration_std", 0.18), click=True)

