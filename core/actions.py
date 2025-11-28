import time
import random
import numpy as np

def wait_gaussian(mean: float, std_ratio: float) -> None:
    d = max(0.01, np.random.normal(mean, mean * std_ratio))
    time.sleep(d)

def inject_distraction(prob: float, long_range: tuple, cap_sec: float = None, warmup_deadline_ts: float = None) -> None:
    if random.uniform(0, 1) < prob:
        lo, hi = long_range
        now_ts = time.time()
        if warmup_deadline_ts and now_ts < warmup_deadline_ts:
            time.sleep(random.uniform(0.4, 1.1))
            return
        d = random.uniform(lo, hi)
        if cap_sec is not None:
            d = min(d, cap_sec)
        time.sleep(d)
