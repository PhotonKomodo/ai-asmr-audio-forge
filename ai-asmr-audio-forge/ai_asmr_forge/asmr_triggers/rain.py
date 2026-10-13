"""Rain bed — layered filtered noise with occasional droplet transients."""
from __future__ import annotations

import numpy as np


class RainBed:
    name = "rain_soft"

    def __init__(self, cutoff_hz: float = 3_200.0, droplets_per_sec: float = 6.0) -> None:
        self._cutoff = cutoff_hz
        self._drops = droplets_per_sec

    def synthesize(self, n_samples: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
        base = rng.standard_normal(n_samples).astype(np.float32)
        alpha = 1.0 - np.exp(-2 * np.pi * self._cutoff / sample_rate)
        # vectorized 1-pole via scipy if available, else numpy cumulative trick
        try:
            from scipy.signal import lfilter
            y = lfilter([alpha], [1.0, -(1.0 - alpha)], base).astype(np.float32)
        except ImportError:
            y = np.cumsum(base) * alpha
            y -= y.mean()

        n_drops = int(self._drops * (n_samples / sample_rate))
        drop_len = int(0.02 * sample_rate)
        env = np.exp(-np.linspace(0, 8.0, drop_len)).astype(np.float32)
        for _ in range(n_drops):
            p = int(rng.integers(0, max(1, n_samples - drop_len)))
            y[p : p + drop_len] += rng.standard_normal(drop_len).astype(np.float32) * env * 0.25
        return y * 0.35


class StormBed(RainBed):
    name = "storm_distant"

    def __init__(self) -> None:
        super().__init__(cutoff_hz=1_800.0, droplets_per_sec=14.0)

    def synthesize(self, n_samples: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
        base = super().synthesize(n_samples, sample_rate, rng)
        # add slow rumble
        t = np.arange(n_samples) / sample_rate
        rumble = (np.sin(2 * np.pi * 38 * t) + 0.5 * np.sin(2 * np.pi * 55 * t)).astype(np.float32)
        return base + rumble * 0.04


def build_triggers() -> list[RainBed]:
    return [RainBed(), StormBed()]