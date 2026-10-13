"""Page-turn trigger — dry paper rustle, modeled as short filtered noise sweeps."""
from __future__ import annotations

import numpy as np


class PageTurnTrigger:
    name = "page_turn"

    def __init__(self, rate_hz: float = 0.4) -> None:
        self._rate = rate_hz

    def synthesize(self, n_samples: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
        out = np.zeros(n_samples, dtype=np.float32)
        rustle_n = int(0.35 * sample_rate)
        env = np.hanning(rustle_n).astype(np.float32)
        mean_gap = int(sample_rate / self._rate)
        pos = 0
        while pos < n_samples - rustle_n:
            pos += int(rng.exponential(mean_gap))
            if pos >= n_samples - rustle_n:
                break
            noise = rng.standard_normal(rustle_n).astype(np.float32)
            # highpass-ish: differentiate to brighten paper
            bright = np.diff(noise, prepend=noise[:1])
            out[pos : pos + rustle_n] += bright * env * 0.22
        return out


def build_triggers() -> list[PageTurnTrigger]:
    return [PageTurnTrigger()]