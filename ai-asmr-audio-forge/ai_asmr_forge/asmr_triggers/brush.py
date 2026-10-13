"""Brush trigger — makeup brush and mic brushing, stochastic grain model."""
from __future__ import annotations

import numpy as np


class BrushTrigger:
    name = "brush_makeup"

    def __init__(self, grain_hz: float = 8_000.0, density: float = 1.0) -> None:
        self._grain_hz = grain_hz
        self._density = density

    def synthesize(self, n_samples: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
        n_grains = int(self._density * (n_samples / sample_rate) * 120.0)
        grains = np.zeros(n_samples, dtype=np.float32)
        grain_len = max(8, int(sample_rate / self._grain_hz * 4))
        env = np.hanning(grain_len).astype(np.float32)
        positions = rng.integers(0, n_samples, size=n_grains)
        for p in positions:
            end = min(p + grain_len, n_samples)
            grains[p:end] += (rng.standard_normal(end - p).astype(np.float32) * env[: end - p]) * 0.08
        return grains


class MicBrushTrigger(BrushTrigger):
    name = "brush_mic"

    def __init__(self) -> None:
        super().__init__(grain_hz=4_000.0, density=2.2)


def build_triggers() -> list[BrushTrigger]:
    return [BrushTrigger(), MicBrushTrigger()]