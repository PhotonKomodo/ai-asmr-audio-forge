"""Tap trigger — fingernail taps on wood, glass, and plastic surfaces."""
from __future__ import annotations

import numpy as np


class TapTrigger:
    name = "tap_wood"

    def __init__(self, rate_hz: float = 1.8, decay_ms: float = 45.0) -> None:
        self._rate = rate_hz
        self._decay_ms = decay_ms

    def synthesize(self, n_samples: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
        out = np.zeros(n_samples, dtype=np.float32)
        decay_n = int(self._decay_ms * 1e-3 * sample_rate)
        env = np.exp(-np.linspace(0, 6.0, decay_n)).astype(np.float32)
        mean_gap = int(sample_rate / self._rate)
        pos = 0
        while pos < n_samples - decay_n:
            pos += int(rng.exponential(mean_gap))
            if pos >= n_samples - decay_n:
                break
            click = rng.standard_normal(decay_n).astype(np.float32) * env
            # wood resonance ~ 220 Hz
            t = np.arange(decay_n) / sample_rate
            click *= np.sin(2 * np.pi * 220 * t).astype(np.float32)
            out[pos : pos + decay_n] += click * 0.4
        return out


class GlassTapTrigger(TapTrigger):
    name = "tap_glass"

    def __init__(self) -> None:
        super().__init__(rate_hz=2.4, decay_ms=120.0)


def build_triggers() -> list[TapTrigger]:
    return [TapTrigger(), GlassTapTrigger()]