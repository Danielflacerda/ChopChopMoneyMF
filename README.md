WillowBot-Draynor (Human‑like, Data‑Driven)

Overview

- Desktop automation framework designed to perform human‑like woodcutting and banking in OSRS.
- Fully configurable via JSON; no code changes required to switch location, tree, detection mode, mouse profile, session length, or pause behavior.

Requirements

- Windows 10/11
- Python 3.9+
- Packages: `opencv-python`, `numpy`, `pyautogui`, `pillow`, `pynput`, `keyboard`, `tkinter` (bundled with Python on Windows)

Install

- `python -m pip install opencv-python numpy pyautogui pillow pynput keyboard`

Project Structure

- `core/` mouse movement, vision, actions, behavior, dashboard, scheduler, window detection
- `strategies/` generic strategy `generic_chop_and_bank.py`
- `configs/` data‑driven JSON files per location/skill
- `assets/` optional template images (`trees/`, `banks/`, `ui/`) for template mode
- `logs/` session logs and daily offline scheduler snapshots

Quick Start

- Open your OSRS client window (e.g., RuneLite) and make sure it’s visible.
- Run with default config: `python main.py`
- Or run with a specific config: `python main.py --config configs/draynor_willows.json`

Window Detection & Resolution Independence

- The bot auto‑detects the game window by title and size and places the overlay outside the game area.
- All ROIs and waypoints are percentage‑based relative to the detected window, so it works at any resolution.

Detection Modes

- Color mode (recommended with highlighted targets): uses HSV color ranges to find marked objects.
- Template mode (fallback): uses multi‑template, multi‑scale matching.
- Switch by setting `"detection": { "mode": "color" | "template" }` in your config.

Key Configuration Fields (example: `configs/draynor_willows.json`)

- `location`: display name, e.g., `"Draynor Village"`
- `window_title`: preferred title to match, e.g., `"RuneLite"`
- `tree_search_region`: ROI relative to window `[rx, ry, rw, rh]`, values 0–1
- `bank_waypoints` / `return_waypoints`: waypoints relative to window, e.g., `[0.39, 0.39]`
- `mouse_profile`: movement profile name, e.g., `"natural_curved"`
- `template_scales`: scales used in template mode, e.g., `[0.9, 1.0, 1.1]`

Color Mode Fields

- `colors.trees_hsv`: list of HSV ranges `[[lowH,lowS,lowV],[highH,highS,highV]]` for tree highlights
- `colors.trees_min_area`: minimum area for tree blobs
- `colors.bank_hsv`: HSV ranges for bank booth highlight
- `colors.bank_min_area`: minimum area for bank blobs
- `colors.deposit_hsv`: HSV ranges for the “deposit all” highlight or button
- `colors.deposit_min_area`: minimum area for deposit blobs

Template Mode Fields (optional)

- `tree_templates`: glob patterns for tree templates, e.g., `"assets/trees/willow_*.png"`
- `bank_templates`: glob patterns for bank booth templates
- `deposit_all_templates`: glob patterns for deposit button templates

Session & Human Behavior

- `run_session.max_minutes`: maximum session duration, bot stops afterward
- `run_session.pause_count`: how many short pauses to perform opportunistically
- `run_session.pause_seconds_range`: range `[min,max]` for short pauses
- `human_behavior.long_break_chance`: chance of a long break per cycle
- `human_behavior.long_break_range`: seconds `[min,max]` for long breaks
- `human_behavior.warmup_seconds`: initial period with micro‑pauses only
- `human_behavior.long_break_soft_cap_sec`: caps long break duration per cycle
- `human_behavior.camera_rotate_every_logs`: camera rotation cadence

Emergency Stop

- Close the OSRS client window or terminate the Python process.

Troubleshooting

- Overlay not visible:
  - Ensure the OSRS window is at least 800×600 and visible.
  - Adjust `window_title` in the config to your exact client window title.
- No detection in color mode:
  - Tune your HSV ranges and `*_min_area` values to match your highlight colors.
  - Confirm the ROI `tree_search_region` covers the area where targets appear.
- No detection in template mode:
  - Provide clean templates and adjust `template_scales` and thresholds.

Example Minimal Config (color mode)

```
{
  "location": "Draynor Village",
  "window_title": "RuneLite",
  "tree_search_region": [0.05, 0.05, 0.5, 0.5],
  "bank_waypoints": [[0.39, 0.39], [0.37, 0.42], [0.36, 0.45]],
  "return_waypoints": [[0.34, 0.46], [0.35, 0.44]],
  "mouse_profile": "natural_curved",
  "detection": { "mode": "color" },
  "colors": {
    "trees_hsv": [[[20, 100, 100], [35, 255, 255]]],
    "trees_min_area": 250,
    "bank_hsv": [[[85, 100, 100], [100, 255, 255]]],
    "bank_min_area": 220,
    "deposit_hsv": [[[140, 120, 120], [160, 255, 255]]],
    "deposit_min_area": 180
  },
  "run_session": {
    "max_minutes": 20,
    "pause_count": 5,
    "pause_seconds_range": [2, 5]
  }
}
```

Notes

- Use responsible settings. The project is for academic study of human‑like automation; do not violate any game’s terms of service.
