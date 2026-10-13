"""MixingBus — fixed-size float32 stereo accumulator with per-add gain/pan."""
from __future__ import annotations

import numpy as np


class MixingBus:
    __slots__ = ("_buf", "_channels", "_samples", "_sr", "_writes")

    def __init__(self, channels: int, samples: int, sample_rate: int) -> None:
        if channels not in (1, 2):
            raise ValueError(f"channels must be 1 or 2, got {channels}")
        if samples <= 0:
            raise ValueError("samples must be > 0")
        self._buf = np.zeros((channels, samples), dtype=np.float32)
        self._channels = channels
        self._samples = samples
        self._sr = sample_rate
        self._writes = 0

    def add(self, source: np.ndarray, gain_db: float, pan: float = 0.0) -> None:
        """Add `source` into the bus. source may be mono [N] or stereo [2,N].

        gain_db is applied linearly. pan is -1 (L) .. +1 (R); ignored for mono
        source when bus is stereo — the mono signal is duplicated.
        """
        src = np.asarray(source, dtype=np.float32)
        if src.ndim == 1:
            src = np.stack([src, src], axis=0)
        if src.shape[0] != self._channels:
            raise ValueError(f"source channels {src.shape[0]} != bus {self._channels}")
        if src.shape[1] > self._samples:
            src = src[:, : self._samples]

        gain = 10.0 ** (gain_db / 20.0)
        n = src.shape[1]

        if self._channels == 2:
            l_gain = gain * (1.0 - max(pan, 0.0))
            r_gain = gain * (1.0 + min(pan, 0.0))
            self._buf[0, :n] += src[0] * l_gain
            self._buf[1, :n] += src[1] * r_gain
        else:
            self._buf[0, :n] += src[0] * gain
        self._writes += 1

    def flush(self) -> np.ndarray:
        return self._buf.copy()

    @property
    def writes(self) -> int:
        return self._writes