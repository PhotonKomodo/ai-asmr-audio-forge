"""Preset schema + loader. A preset is a named render graph fragment."""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class TriggerLayer(BaseModel):
    trigger: str
    gain_db: float = Field(default=-12.0, ge=-60.0, le=0.0)
    pan: float = Field(default=0.0, ge=-1.0, le=1.0)
    density: float = Field(default=1.0, ge=0.0, le=8.0)


class Preset(BaseModel):
    name: str
    description: str = ""
    duration_seconds: float = Field(default=120.0, gt=0.0, le=3600.0)
    bed: str = "rain_soft"
    layers: list[TriggerLayer] = Field(default_factory=list)


def load_preset(path: Path) -> Preset:
    data = yaml.safe_load(path.read_text("utf-8"))
    return Preset.model_validate(data)


def load_all_presets(directory: Path) -> dict[str, Preset]:
    out: dict[str, Preset] = {}
    for p in sorted(directory.glob("*.yaml")):
        preset = load_preset(p)
        out[preset.name] = preset
    return out