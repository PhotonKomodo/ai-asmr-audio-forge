"""Top-level entrypoint. Wires config -> engine -> trigger registry -> UI.

Called by `ai-asmr-forge` console script and by `python -m ai_asmr_forge.app`.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from rich.logging import RichHandler

from ai_asmr_forge.bootstrap.env_probe import probe_environment
from ai_asmr_forge.config.settings import ForgeSettings
from ai_asmr_forge.core.render_engine import RenderEngine
from ai_asmr_forge.services.checkpoint_store import CheckpointStore
from ai_asmr_forge.ui.cli import build_cli


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=False)],
    )


def run(argv: list[str] | None = None) -> int:
    """Parse argv, boot the engine, hand off to the CLI command tree."""
    argv = list(sys.argv[1:] if argv is None else argv)

    cli = build_cli()
    # Click handles --help / --version itself; we pre-parse only our own flags.
    opts = cli.make_context("ai-asmr-forge", argv, resilient_parsing=True)

    settings = ForgeSettings.load()

    if opts.params.get("dry_run"):
        _configure_logging(verbose=True)
        logging.getLogger(__name__).info("dry-run: settings ok -> %s", settings.model_dump())
        return 0

    _configure_logging(verbose=bool(opts.params.get("verbose")))
    log = logging.getLogger(__name__)

    probe = probe_environment()
    log.info("env: %s", probe.summary())

    store = CheckpointStore(root=Path(settings.model_dir))
    store.ensure_default_checkpoints()

    engine = RenderEngine(settings=settings, checkpoints=store)
    cli.obj = {"engine": engine, "settings": settings, "log": log}

    try:
        return cli.main(args=argv, standalone_mode=False) or 0
    except Exception as exc:  # noqa: BLE001 — final boundary, log and exit
        log.exception("fatal: %s", exc)
        return 1