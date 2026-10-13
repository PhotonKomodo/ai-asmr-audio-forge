"""Runtime settings. Loads config/default.toml, then overlays config/local.toml."""
from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
DEFAULT_TOML = CONFIG_DIR / "default.toml"
LOCAL_TOML = CONFIG_DIR / "local.toml"


class ForgeSettings(BaseSettings):
    """All knobs the engine reads. Values come from TOML, then env `AIAF_*`."""

    model_config = SettingsConfigDict(env_prefix="AIAF_", extra="ignore")

    sample_rate: int = Field(default=48_000, ge=8_000, le=192_000)
    bit_depth: int = Field(default=24, ge=16, le=32)
    master_gain_db: float = Field(default=-6.0, ge=-24.0, le=0.0)
    peak_ceiling_dbfs: float = Field(default=-0.3, ge=-6.0, le=0.0)
    render_dir: Path = Field(default=Path("renders"))
    model_dir: Path = Field(default=Path("model_cache"))
    default_preset: str = "whisper_rain_bed"
    max_render_seconds: int = Field(default=900, ge=1, le=7200)
    thread_count: int = Field(default=0, ge=0, le=64)  # 0 = auto
    allow_plugins: bool = False

    @classmethod
    def load(cls) -> "ForgeSettings":
        raw: dict = {}
        if DEFAULT_TOML.exists():
            raw.update(tomllib.loads(DEFAULT_TOML.read_text("utf-8")))
        if LOCAL_TOML.exists():
            raw.update(tomllib.loads(LOCAL_TOML.read_text("utf-8")))
        return cls(**raw)