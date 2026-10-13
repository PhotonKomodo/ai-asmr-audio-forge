"""Whisper trigger — binaural soft-spoken ASMR via a tiny neural vocoder stub.

In production this calls a distilled whisper-vocoder checkpoint served by
`services/checkpoint_store.py`. If the checkpoint is missing, we fall back to
a formant-shaped noise burst so the render graph never dead-ends.
"""
from __future__ import annotations

import numpy as np


class WhisperTrigger:
    name = "whisper_soft"

    def __init__(self, phrase_len_s: float = 1.4, seed_bank: int = 64) -> None:
        self._phrase_len = phrase_len_s
        self._seed_bank = seed_bank

    def synthesize(self, n_samples: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
        out = np.zeros(n_samples, dtype=np.float32)
        phrase_n = int(self._phrase_len * sample_rate)
        pos = 0
        while pos < n_samples:
            burst = self._one_whisper(phrase_n, sample_rate, rng)
            end = min(pos + phrase_n, n_samples)
            out[pos:end] += burst[: end - pos]
            pos += phrase_n + int(rng.uniform(0.2, 0.9) * sample_rate)
        return out

    def _one_whisper(self, n: int, sr: int, rng: np.random.Generator) -> np.ndarray:
        noise = rng.standard_normal(n).astype(np.float32)
        # formant shaping: two bandpass-ish envelopes around 1.2k and 3.4k
        t = np.arange(n) / sr
        f1 = 1200 + 400 * np.sin(2 * np.pi * 0.7 * t)
        f2 = 3400 + 600 * np.sin(2 * np.pi * 1.1 * t + 1.3)
        env = 0.5 * np.sin(2 * np.pi * f1 * t) + 0.3 * np.sin(2 * np.pi * f2 * t)
        window = np.hanning(n).astype(np.float32)
        return (noise * env * window * 0.18).astype(np.float32)


class BreathTrigger:
    name = "breath_soft"

    def synthesize(self, n_samples: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
        noise = rng.standard_normal(n_samples).astype(np.float32)
        # 1-pole lowpass at ~900 Hz
        alpha = 1.0 - np.exp(-2 * np.pi * 900 / sample_rate)
        y = np.empty_like(noise)
        acc = 0.0
        for i in range(n_samples):
            acc += alpha * (noise[i] - acc)
            y[i] = acc
        return y * 0.12


def build_triggers() -> list[WhisperTrigger | BreathTrigger]:
    return [WhisperTrigger(), BreathTrigger()]