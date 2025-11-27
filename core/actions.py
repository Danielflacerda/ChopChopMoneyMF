import time
import random
import numpy as np

def wait_gaussian(mean: float, std_ratio: float) -> None:
    d = max(0.01, np.random.normal(mean, mean * std_ratio))
    time.sleep(d)

def inject_distraction(prob: float, long_range: tuple) -> None:
    if random.uniform(0, 1) < prob:
        lo, hi = long_range
        time.sleep(random.uniform(lo, hi))

