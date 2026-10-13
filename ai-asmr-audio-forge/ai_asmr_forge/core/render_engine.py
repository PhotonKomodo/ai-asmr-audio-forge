"""RenderEngine — top-level orchestrator for a single ASMR render job.

The engine owns:
  * the trigger registry (what sounds can be synthesized)
  * the mixing bus (float32, [channels, samples], -1.0..1.0 nominal)
  * the mastering chain (gain, soft-knee limiter, dither on export)

Threading model: single render thread. Trigger synthesis may fan out to a
ProcessPoolExecutor when `settings.thread_count > 1`. The mixing bus is not
thread-safe; all writes happen on the render thread after futures resolve.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

from ai_asmr_forge.config.presets import Preset
from ai_asmr_forge.config.settings import ForgeSettings
from ai_asmr_forge.core.mixing_bus import MixingBus
from ai_asmr_forge.core.mastering import master_chain
from ai_asmr_forge.services.checkpoint_store import CheckpointStore
from ai_asmr_forge.asmr_triggers.registry import TriggerRegistry

log = logging.getLogger(__name__)


@dataclass(slots=True)
class RenderJob:
    preset: Preset
    seed: int = 0
    prompt: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class RenderResult:
    samples: np.ndarray  # float32, shape [channels, samples]
    sample_rate: int
    peak_dbfs: float
    duration_seconds: float


class RenderEngine:
    def __init__(self, settings: ForgeSettings, checkpoints: CheckpointStore) -> None:
        self.settings = settings
        self.checkpoints = checkpoints
        self.registry = TriggerRegistry.default()
        self._rng = np.random.default_rng(0)

    def render(self, job: RenderJob) -> RenderResult:
        sr = self.settings.sample_rate
        n_samples = int(job.preset.duration_seconds * sr)
        bus = MixingBus(channels=2, samples=n_samples, sample_rate=sr)

        log.info("render: preset=%s dur=%.1fs sr=%d", job.preset.name, job.preset.duration_seconds, sr)

        bed = self.registry.get(job.preset.bed)
        bus.add(bed.synthesize(n_samples, sr, self._rng), gain_db=-18.0, pan=0.0)

        for layer in job.preset.layers:
            trig = self.registry.get(layer.trigger)
            events = trig.synthesize(n_samples, sr, self._rng)
            bus.add(events, gain_db=layer.gain_db, pan=layer.pan)

        mixed = bus.flush()
        mastered = master_chain(
            mixed,
            sample_rate=sr,
            master_gain_db=self.settings.master_gain_db,
            ceiling_dbfs=self.settings.peak_ceiling_dbfs,
        )

        peak = float(np.max(np.abs(mastered))) if mastered.size else 0.0
        peak_dbfs = 20.0 * np.log10(max(peak, 1e-9))
        return RenderResult(
            samples=mastered,
            sample_rate=sr,
            peak_dbfs=peak_dbfs,
            duration_seconds=mastered.shape[-1] / sr,
        )