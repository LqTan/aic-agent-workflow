"""AIC backend CLI entry points — mirrors ``npm run`` semantics.

Usage (run from ``backend/``)::

    uv run aic-dev               # uvicorn dev server on 0.0.0.0:8000 with --reload
    uv run aic-prepare-data      # generate manifest.csv + collection.json under ./data
    uv run aic-build-index       # build hybrid R-tree index at ./data/search_index
    uv run aic-lint              # ruff check src tests
    uv run aic-test              # pytest

Note: ``aic-lint`` and ``aic-test`` require the dev extras::

    uv sync --extra dev
"""

from __future__ import annotations

from pathlib import Path

import uvicorn
from dotenv import load_dotenv


def _load_dotenv_once() -> None:
    """Load ``.env`` into ``os.environ`` so legacy ``os.getenv()`` calls work.

    pydantic-settings reads ``.env`` into its own ``Settings`` object but does
    not export to ``os.environ`` — without this, modules like
    ``indexer.get_index()`` and ``embedding.ClipTextEncoder`` that call
    ``os.getenv("KIS_*")`` would miss the values.
    """
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def serve() -> None:
    """Run the FastAPI app on 0.0.0.0:8000 with hot reload."""
    _load_dotenv_once()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


def prepare_data() -> None:
    """Generate ``manifest.csv`` (+ collection.json) under ``./data``."""
    from app.features.data_pipeline.cli import main as pipeline_cli

    raise SystemExit(pipeline_cli(["prepare-data", "--data-root", "./data"]))


def build_index() -> None:
    """Build the hybrid R-tree index from ``./data`` into ``./data/search_index``.

    Runs ``prepare-data`` first so ``manifest.csv`` is always in sync before
    the heavy ``build-index`` step starts.
    """
    from app.features.data_pipeline.cli import main as pipeline_cli
    from app.features.search_engine.cli import main as engine_cli

    raise SystemExit(
        pipeline_cli(
            ["prepare-data", "--data-root", "./data"]
        )
        or engine_cli(
            [
                "build-index",
                "--data-root",
                "./data",
                "--index-dir",
                "./data/search_index",
            ]
        )
    )


def lint() -> None:
    """Run ``ruff check`` over ``src`` and ``tests``."""
    import subprocess
    import sys

    raise SystemExit(
        subprocess.call(
            [sys.executable, "-m", "ruff", "check", "src", "tests"],
            cwd=Path(__file__).resolve().parents[2],
        )
    )


def test() -> None:
    """Run ``pytest``."""
    import subprocess
    import sys

    raise SystemExit(
        subprocess.call(
            [sys.executable, "-m", "pytest"],
            cwd=Path(__file__).resolve().parents[2],
        )
    )
