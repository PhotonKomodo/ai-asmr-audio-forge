"""TriggerRegistry — name -> Trigger instance map with a default catalogue."""
from __future__ import annotations

from typing import Protocol

import numpy as np


class Trigger(Protocol):
    name: str

    def synthesize(
        self,
        n_samples: int,
        sample_rate: int,
        rng: np.random.Generator,
    ) -> np.ndarray: ...


class TriggerRegistry:
    def __init__(self) -> None:
        self._triggers: dict[str, Trigger] = {}

    def register(self, trigger: Trigger) -> None:
        if not trigger.name:
            raise ValueError("trigger.name must be set")
        self._triggers[trigger.name] = trigger

    def get(self, name: str) -> Trigger:
        try:
            return self._triggers[name]
        except KeyError as exc:
            raise KeyError(f"unknown trigger '{name}'. known: {sorted(self._triggers)}") from exc

    def names(self) -> list[str]:
        return sorted(self._triggers)

    @classmethod
    def default(cls) -> "TriggerRegistry":
        from ai_asmr_forge.asmr_triggers import (
            brush, keyboard, page_turn, rain, tap, whisper,
        )
        reg = cls()
        for mod in (whisper, tap, brush, rain, page_turn, keyboard):
            for t in mod.build_triggers():
                reg.register(t)
        return reg