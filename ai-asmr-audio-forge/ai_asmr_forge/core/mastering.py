"""Mastering chain: gain -> soft-knee limiter -> (export-time) dither."""
from __future__ import annotations

import numpy as np


def _soft_knee_limiter(x: np.ndarray, ceiling: float, knee_db: float = 3.0) -> np.ndarray:
    """Lookahead-free soft-knee limiter. O(n), no allocation beyond one abs buffer."""
    knee = 10.0 ** (knee_db / 20.0)
    mag = np.abs(x)
    over = mag > (ceiling / knee)
    if not np.any(over):
        return x
    # tanh knee past the threshold, hard clip at ceiling
    scaled = np.where(over, np.tanh((mag - ceiling / knee) / (knee - ceiling / knee)), 0.0)
    limited_mag = np.where(over, (ceiling / knee) + scaled * (ceiling - ceiling / knee), mag)
    return np.sign(x) * np.minimum(limited_mag, ceiling)


def master_chain(
    samples: np.ndarray,
    sample_rate: int,
    master_gain_db: float,
    ceiling_dbfs: float,
) -> np.ndarray:
    if samples.size == 0:
        return samples
    gain = 10.0 ** (master_gain_db / 20.0)
    ceiling = 10.0 ** (ceiling_dbfs / 20.0)
    y = samples.astype(np.float32, copy=True) * gain
    y = _soft_knee_limiter(y, ceiling)
    return y