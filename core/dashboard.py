import time
from typing import List
import tkinter as tk

class Overlay:
    def __init__(self, position=(50, 50)):
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.7)
        self.root.overrideredirect(True)
        self.root.geometry(f"400x160+{position[0]}+{position[1]}")
        self.label = tk.Label(self.root, text="Status: Idle\nXP/h: --\nLogs: 0", justify="left")
        self.label.pack(fill="both", expand=True)
        self._running = False

    def update(self, lines: List[str]):
        self.label.config(text="\n".join(lines))
        self.root.update_idletasks()
        self.root.update()

    def start(self):
        self._running = True
        self.update(["Status: Iniciando", "XP/h: --", "Logs: 0"]) 

