import json
import random
import datetime as dt
from pathlib import Path
from typing import List, Tuple

def _seed_for_today() -> int:
    today = dt.date.today()
    return int(today.strftime("%Y%m%d"))

def make_blocks(total_minutes: int = 360, blocks_range: Tuple[int, int] = (8, 14)) -> List[Tuple[dt.datetime, dt.datetime]]:
    random.seed(_seed_for_today())
    now = dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    n = random.randint(blocks_range[0], blocks_range[1])
    minutes_left = total_minutes
    blocks = []
    for _ in range(n):
        if minutes_left <= 0:
            break
        max_dur = min(210, minutes_left)
        if max_dur < 3:
            dur = minutes_left
        else:
            dur = random.randint(3, max_dur)
        start_min = random.randint(0, 24 * 60 - dur)
        start = now + dt.timedelta(minutes=start_min)
        end = start + dt.timedelta(minutes=dur)
        blocks.append((start, end))
        minutes_left -= dur
    blocks.sort(key=lambda x: x[0])
    return blocks

def persist_blocks(blocks: List[Tuple[dt.datetime, dt.datetime]], path: str = "logs/scheduler_today.json") -> None:
    Path("logs").mkdir(parents=True, exist_ok=True)
    data = [[b[0].isoformat(), b[1].isoformat()] for b in blocks]
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump({"blocks": data}, f, ensure_ascii=False, indent=2)

def is_offline_now(blocks: List[Tuple[dt.datetime, dt.datetime]]) -> bool:
    now = dt.datetime.now()
    for s, e in blocks:
        if s <= now <= e:
            return True
    return False
