import json
from pathlib import Path

def load_config(path: str = "config/config.json") -> dict:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

