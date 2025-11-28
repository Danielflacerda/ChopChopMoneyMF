import random
import time
from typing import Dict, Optional, Tuple, List

import numpy as np

from core.movement import MovementEngine, human_click
from core.vision import TemplateMatcher, load_templates
from core.actions import wait_gaussian, inject_distraction
from core.dashboard import Overlay
from core.scheduler import make_blocks, persist_blocks, is_offline_now
from core.window import detect_game_roi, to_abs_rect, to_abs_point
from pathlib import Path
import json
import datetime as dt

class Command:
    def execute(self) -> None:
        raise NotImplementedError

class CutTree(Command):
    def __init__(self, cfg: Dict, matcher: TemplateMatcher, engine: MovementEngine):
        self.cfg = cfg
        self.matcher = matcher
        self.engine = engine
        self.templates = load_templates(cfg.get("tree_templates", []))

    def execute(self) -> Optional[Tuple[int, int, int, int]]:
        root = detect_game_roi(title_candidates=[self.cfg.get("window_title", "RuneLite")])
        rel_roi = tuple(self.cfg.get("tree_search_region", [0.0, 0.0, 1.0, 1.0]))
        roi = to_abs_rect(root, rel_roi)
        thr = float(self.cfg.get("tree_threshold", 0.68))
        scales = self.cfg.get("template_scales", [0.9, 1.0, 1.1])
        hit = self.matcher.find(self.templates, roi, thr, scales=scales)
        if hit:
            x, y, w, h, _ = hit
            cx = int(np.random.normal(x + w // 2, self.cfg.get("click_offset", 15) * 0.45))
            cy = int(np.random.normal(y + h // 2, self.cfg.get("click_offset", 15) * 0.45))
            human_click(cx, cy, self.cfg.get("mouse_profile", "natural_curved"), self.cfg)
            return (x, y, w, h)
        return None

class WalkWaypoints(Command):
    def __init__(self, cfg: Dict, engine: MovementEngine, waypoints_key: str):
        self.cfg = cfg
        self.engine = engine
        self.key = waypoints_key

    def execute(self) -> None:
        wps: List[List[float]] = self.cfg.get(self.key, [])
        root = detect_game_roi(title_candidates=[self.cfg.get("window_title", "RuneLite")])
        for wp in wps:
            px, py = to_abs_point(root, (wp[0], wp[1]))
            x = int(np.random.normal(px, 30))
            y = int(np.random.normal(py, 30))
            self.engine.move(self.cfg.get("mouse_profile", "natural_curved"), x, y, self.cfg, click=True)
            wait_gaussian(0.9, 0.35)

class DepositAll(Command):
    def __init__(self, cfg: Dict, matcher: TemplateMatcher, engine: MovementEngine):
        self.cfg = cfg
        self.matcher = matcher
        self.engine = engine
        self.bank_templates = load_templates(cfg.get("bank_templates", []))
        self.deposit_templates = load_templates(cfg.get("deposit_all_templates", []))

    def execute(self) -> None:
        root = detect_game_roi(title_candidates=[self.cfg.get("window_title", "RuneLite")])
        rel_roi = tuple(self.cfg.get("tree_search_region", [0.0, 0.0, 1.0, 1.0]))
        roi = to_abs_rect(root, rel_roi)
        thr = float(self.cfg.get("bank_threshold", 0.7))
        bank = self.matcher.find(self.bank_templates, roi, thr, scales=self.cfg.get("template_scales", [0.9, 1.0, 1.1]))
        if bank:
            x, y, w, h, _ = bank
            self.engine.move(self.cfg.get("mouse_profile", "natural_curved"), int(np.random.normal(x + w // 2, 7)), int(np.random.normal(y + h // 2, 7)), self.cfg, click=True)
            wait_gaussian(1.8, 0.25)
        dep_thr = float(self.cfg.get("deposit_threshold", 0.7))
        dep = self.matcher.find(self.deposit_templates, roi, dep_thr, scales=self.cfg.get("template_scales", [0.9, 1.0, 1.1]))
        if dep:
            x, y, w, h, _ = dep
            self.engine.move(self.cfg.get("mouse_profile", "natural_curved"), int(np.random.normal(x + w // 2, 6)), int(np.random.normal(y + h // 2, 6)), self.cfg, click=True)
            wait_gaussian(1.2, 0.25)

class GenericChopAndBank:
    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self.matcher = TemplateMatcher()
        self.engine = MovementEngine()
        root = detect_game_roi(title_candidates=[cfg.get("window_title", "RuneLite")])
        ox = root[0] + root[2] + 20
        oy = root[1] + 20
        self.overlay = Overlay(position=tuple(cfg.get("overlay_position", [ox, oy])))
        self.root_win = root
        now = dt.datetime.now()
        self.session = {"logs_cut": 0, "start": now.isoformat(), "actions": []}
        self._start_ts = now.timestamp()
        self.blocks = make_blocks()
        persist_blocks(self.blocks)

    def run(self) -> None:
        self.overlay.start()
        count = 0
        lo, hi = self.cfg.get("human_behavior", {}).get("camera_rotate_every_logs", [3, 7])
        rotate_each = random.randint(int(lo), int(hi))
        try:
            while True:
                if is_offline_now(self.blocks):
                    self.overlay.update(["Status: Offline programado", "XP/h: --", f"Logs: {self.session['logs_cut']}"]) 
                    time.sleep(5)
                    continue
                hb = self.cfg.get("human_behavior", {})
                warmup_sec = float(hb.get("warmup_seconds", 90))
                cap = float(hb.get("long_break_soft_cap_sec", 1.5))
                inject_distraction(hb.get("long_break_chance", 0.12), tuple(hb.get("long_break_range", [7, 22])), cap_sec=cap, warmup_deadline_ts=self._start_ts + warmup_sec)
                hit = CutTree(self.cfg, self.matcher, self.engine).execute()
                if hit:
                    count += 1
                    self.session["logs_cut"] += 1
                    self.session["actions"].append({"t": dt.datetime.now().isoformat(), "action": "cut"})
                    self.overlay.update(["Status: Cortando", "XP/h: --", f"Logs: {self.session['logs_cut']}"]) 
                    wait_gaussian(4.0, 0.18)
                if count % rotate_each == 0 and count > 0:
                    count += 1
                if self.cfg.get("bank_waypoints") and (self.session["logs_cut"] % 28 == 0) and self.session["logs_cut"] > 0:
                    self.overlay.update(["Status: Indo ao banco", "XP/h: --", f"Logs: {self.session['logs_cut']}"]) 
                    WalkWaypoints(self.cfg, self.engine, "bank_waypoints").execute()
                    DepositAll(self.cfg, self.matcher, self.engine).execute()
                    self.overlay.update(["Status: Retornando ao spot", "XP/h: --", f"Logs: {self.session['logs_cut']}"]) 
                    WalkWaypoints(self.cfg, self.engine, "return_waypoints").execute()
        finally:
            Path("logs").mkdir(parents=True, exist_ok=True)
            with Path(f"logs/session_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json").open("w", encoding="utf-8") as f:
                json.dump(self.session, f, ensure_ascii=False, indent=2)
