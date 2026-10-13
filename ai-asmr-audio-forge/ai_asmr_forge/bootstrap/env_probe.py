"""Probes the host for audio backend, torch device, and ffmpeg availability."""
from __future__ import annotations

import platform
import shutil
from dataclasses import dataclass

import sounddevice as sd
import torch


@dataclass(frozen=True, slots=True)
class EnvironmentProbe:
    os_name: str
    python: str
    torch_device: str
    cuda_available: bool
    audio_devices: int
    ffmpeg_present: bool

    def summary(self) -> str:
        return (
            f"os={self.os_name} py={self.python} "
            f"device={self.torch_device} cuda={self.cuda_available} "
            f"audio_out={self.audio_devices} ffmpeg={self.ffmpeg_present}"
        )


def probe_environment() -> EnvironmentProbe:
    cuda = torch.cuda.is_available()
    device = "cuda" if cuda else "cpu"
    try:
        n_devices = len(sd.query_devices())
    except Exception:  # noqa: BLE001 — PortAudio can raise on locked-down hosts
        n_devices = 0
    return EnvironmentProbe(
        os_name=f"{platform.system()} {platform.release()}",
        python=platform.python_version(),
        torch_device=device,
        cuda_available=cuda,
        audio_devices=n_devices,
        ffmpeg_present=shutil.which("ffmpeg") is not None,
    )