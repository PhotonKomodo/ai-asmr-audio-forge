# Contributing to ai-asmr-audio-forge

Thanks for wanting to make tingles with us. This repo is a Windows desktop
tool that generates AI-driven ASMR audio — whispers, tapping, brushing,
rain, page turns, keyboard clacks, and layered ambience — from text prompts
and reference stems.

## Ground rules

- Python 3.11+ only. We use `tomllib`, `match`, and `ExceptionGroup`.
- Every DSP module ships with a unit test. No test, no merge.
- New trigger voices go through `asmr_triggers/` and register in
  `asmr_triggers/registry.py`. Do not monkeypatch the render graph.
- Audio must never clip. If your peak exceeds -0.3 dBFS, your PR is
  rejected on sight.

## Dev setup

```
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests/ -q
python -m ai_asmr_forge.app --dry-run
```

## Style

- `ruff` and `black` on save. Line length 100.
- Type hints everywhere. `mypy --strict` on `ai_asmr_forge/core/`.
- Docstrings: one line for private, full Google-style for public.

## Commit messages

`[core]`, `[trigger]`, `[ui]`, `[dsp]`, `[docs]` prefixes. Keep them short.

## Reporting bugs

Open an issue with: Windows build, Python version, model checkpoint hash,
input prompt, and the rendered WAV (or its spectrogram if the file is huge).