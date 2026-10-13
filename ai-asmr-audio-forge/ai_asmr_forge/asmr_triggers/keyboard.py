"""Keyboard trigger — mechanical clacks, per-key timbre variation."""
from __future__ import annotations

import numpy as np


class KeyboardTrigger:
    name = "keyboard_mech"

    def __init__(self, wpm: float = 80.0) -> None:
        self._wpm = wpm

    def synthesize(self, n_samples: int, sample_rate: int,