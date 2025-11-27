import random
import time
from typing import Dict, Optional, Tuple

import numpy as np
import pyautogui
import keyboard

from src.movement import move_mouse_curved, random_point_in_bbox
from src.vision import TemplateMatcher, load_templates, is_idle

class WillowBot:
    def __init__(self, config: Dict):
        self.config = config
        self.matcher = TemplateMatcher()
        self.tree_templates = load_templates(config.get("templates", {}).get("trees", []))
        self.bank_templates = load_templates(config.get("templates", {}).get("bank", []))
        self.deposit_templates = load_templates(config.get("templates", {}).get("deposit_all", []))
        self.roi_game = tuple(config.get("roi", {}).get("game", [0, 0, 1920, 1080]))
        self.movement_profile = config.get("movement_profiles", {}).get(config.get("movement_profile", "casual"), {})
        self.click_offset = int(config.get("click_offset_pixels", 15))

    def _human_pause(self) -> None:
        chance = random.uniform(0, 1)
        pmin, pmax = self.config.get("behavior", {}).get("long_pause_prob", [0.08, 0.15])
        if chance < random.uniform(pmin, pmax):
            dmin, dmax = self.config.get("behavior", {}).get("long_pause_seconds", [5.0, 18.0])
            time.sleep(random.uniform(dmin, dmax))

    def _mouse_lose_focus(self) -> None:
        chance = random.uniform(0, 1)
        pmin, pmax = self.config.get("behavior", {}).get("lose_focus_prob", [0.02, 0.05])
        if chance < random.uniform(pmin, pmax):
            w = self.roi_game[2]
            y = self.roi_game[1] + random.randint(0, self.roi_game[3] - 1)
            x = self.roi_game[0] + w + random.randint(10, 80)
            move_mouse_curved((x, y), self.movement_profile, click=False)

    def _wait_cut_animation(self) -> None:
        lo, hi = self.config.get("timers", {}).get("cut_animation_seconds", [3.5, 4.8])
        time.sleep(random.uniform(lo, hi))

    def _rotate_camera(self) -> None:
        lo, hi = self.config.get("behavior", {}).get("camera_rotation_degrees", [10, 25])
        deg = random.uniform(lo, hi)
        start = pyautogui.position()
        dx = int(np.random.normal(deg * 4.0, deg))
        dy = int(np.random.normal(0.0, deg * 0.35))
        end = (start.x + dx, start.y + dy)
        pyautogui.mouseDown(button="right")
        move_mouse_curved(end, self.movement_profile, click=False)
        pyautogui.mouseUp(button="right")

    def _find_tree(self) -> Optional[Tuple[int, int, int, int, float]]:
        if not self.tree_templates:
            return None
        thr = float(self.config.get("thresholds", {}).get("tree", 0.68))
        return self.matcher.find(self.tree_templates, self.roi_game, thr)

    def _click_bbox(self, bbox: Tuple[int, int, int, int]) -> None:
        miss_chance = 0.03
        if random.uniform(0, 1) < miss_chance:
            x, y, w, h = bbox
            ox = int(np.random.normal(0, 24))
            oy = int(np.random.normal(0, 24))
            px = max(0, x + w // 2 + ox)
            py = max(0, y + h // 2 + oy)
            move_mouse_curved((px, py), self.movement_profile, click=True)
        else:
            pt = random_point_in_bbox(bbox, self.click_offset)
            move_mouse_curved(pt, self.movement_profile, click=True)

    def _inventory_full(self) -> bool:
        roi = tuple(self.config.get("roi", {}).get("inventory_last_slot", [1600, 820, 42, 36]))
        idle = is_idle(roi, duration_ms=120, threshold=self.config.get("thresholds", {}).get("idle_inventory_threshold", 8.0))
        return not idle

    def _navigate_to_bank_and_deposit(self) -> None:
        thr = float(self.config.get("thresholds", {}).get("bank", 0.7))
        bank = None
        if self.bank_templates:
            bank = self.matcher.find(self.bank_templates, self.roi_game, thr)
        if bank:
            self._click_bbox((bank[0], bank[1], bank[2], bank[3]))
            time.sleep(random.uniform(1.4, 2.4))
        if self.deposit_templates:
            dep_thr = float(self.config.get("thresholds", {}).get("deposit_all", 0.7))
            dep = self.matcher.find(self.deposit_templates, self.roi_game, dep_thr)
            if dep:
                self._click_bbox((dep[0], dep[1], dep[2], dep[3]))
                time.sleep(random.uniform(1.0, 1.8))

    def _return_to_spot(self) -> None:
        waypoints = self.config.get("waypoints", {}).get("return_spot", [])
        for wp in waypoints:
            x = int(np.random.normal(wp[0], 30))
            y = int(np.random.normal(wp[1], 30))
            move_mouse_curved((x, y), self.movement_profile, click=True)
            time.sleep(random.uniform(0.6, 1.2))

    def run(self) -> None:
        count = 0
        rotate_each = random.randint(3, 8)
        stop_key = self.config.get("hotkeys", {}).get("stop", "F12")
        while True:
            if keyboard.is_pressed(stop_key):
                break
            tree = self._find_tree()
            if tree:
                self._click_bbox((tree[0], tree[1], tree[2], tree[3]))
                self._wait_cut_animation()
                self._human_pause()
                self._mouse_lose_focus()
                count += 1
                if count % rotate_each == 0:
                    self._rotate_camera()
            idle_roi = tuple(self.config.get("roi", {}).get("idle_character", [900, 450, 120, 160]))
            if is_idle(idle_roi, duration_ms=int(np.random.uniform(800, 1400)), threshold=self.config.get("thresholds", {}).get("idle_motion_threshold", 4.0)):
                pass
            if self._inventory_full():
                self._navigate_to_bank_and_deposit()
                self._return_to_spot()
            time.sleep(random.uniform(0.05, 0.25))
