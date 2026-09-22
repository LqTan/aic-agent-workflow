"""End-to-end test against the AIC L21 subset.

This test runs only when:
  1. The dataset is present at ``../data`` (so we have real keyframes).
  2. The ``[hybrid]`` extra is installed (torch + open_clip_torch) — required
     to actually encode queries through CLIP and load the R-tree index.

In CI without these dependencies the test is auto-skipped.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("torch", reason="Real search needs torch from [hybrid] extra.")
pytest.importorskip("open_clip", reason="Real search needs open_clip_torch from [hybrid] extra.")
pytest.importorskip("rtree", reason="Real search needs rtree (already core, but cheap to check).")

from fastapi.testclient import TestClient  # noqa: E402

DATASET_ROOT = Path(__file__).resolve().parents[2] / "data"
INDEX_DIR = Path(__file__).resolve().parents[1] / "data" / "search_index"


pytestmark = pytest.mark.skipif(
    not (DATASET_ROOT / "clip-features-32").is_dir(),
    reason=f"AIC dataset not found at {DATASET_ROOT}; skipping real-search test.",
)


@pytest.fixture(scope="module")
def search_index(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a fresh search index from the L21 subset."""
    from app.features.search_engine.builder import BuildOptions, build_search_index
    from app.features.search_engine.manifest import build_manifest

    workdir = tmp_path_factory.mktemp("real_search_index")
    for sub in ("keyframes", "map-keyframes", "objects", "videos", "clip-features-32"):
        src = DATASET_ROOT / sub
        if src.is_dir():
            shutil.copytree(src, workdir / sub)

    manifest_info = build_manifest(workdir)
    build_search_index(
        data_root=workdir,
        manifest_path=manifest_info["output"],
        index_dir=workdir / "search_index",
        options=BuildOptions(
            pca_dimensions=24,
            pca_sample_size=50_000,
            domains_per_frame=2,
            object_min_score=0.25,
        ),
    )
    return workdir / "search_index"


@pytest.fixture(scope="module")
def client(search_index: Path, monkeypatch_module) -> TestClient:  # type: ignore[no-untyped-def]
    from app.core.config import get_settings
    from app.main import create_app

    monkeypatch_module.setenv("KIS_DEMO_MODE", "false")
    monkeypatch_module.setenv("KIS_DATA_ROOT", str(search_index.parent))
    monkeypatch_module.setenv("KIS_INDEX_ROOT", str(search_index))
    get_settings.cache_clear()

    return TestClient(create_app())


@pytest.fixture(scope="module")
def monkeypatch_module():
    from _pytest.monkeypatch import MonkeyPatch

    mp = MonkeyPatch()
    yield mp
    mp.undo()


def test_real_search_returns_enriched_results(client: TestClient) -> None:
    response = client.post(
        "/api/v1/kis/search/",
        json={
            "query": "người đi xe đạp ngoài đường",
            "collection_ids": [],
            "top_k": 3,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["count"] >= 1
    first = body["results"][0]
    for required in (
        "rank",
        "keyframe_id",
        "collection_id",
        "video_id",
        "frame_number",
        "timestamp_ms",
        "image_path",
        "video_path",
        "image_url",
        "video_url",
        "score",
    ):
        assert required in first, f"missing field {required}"
    assert first["image_url"].startswith("http")
    assert first["video_url"].startswith("http")
    assert first["image_url"].endswith(first["image_path"])
    assert first["video_url"].endswith(first["video_path"])


def test_real_agent_search_persists_run(client: TestClient) -> None:
    response = client.post(
        "/api/v1/kis/agent/search/",
        json={
            "query": "người đi xe đạp",
            "collection_ids": [],
            "top_k": 3,
            "quality_threshold": 0.3,
            "max_attempts": 2,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert "decision" in body
    assert body["decision"] in {"accepted", "best_effort"}
    assert body["count"] >= 1
    assert any(
        "object_bow" in (item.get("score_components") or {})
        for item in body["results"]
    )


def test_cli_prepare_data_runs(monkeypatch_module, tmp_path: Path) -> None:
    """Smoke-test the ``prepare-data`` CLI against the real dataset."""
    workdir = tmp_path / "data"
    workdir.mkdir()
    for sub in ("keyframes", "map-keyframes", "objects", "videos", "clip-features-32"):
        src = DATASET_ROOT / sub
        if src.is_dir():
            shutil.copytree(src, workdir / sub)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.features.data_pipeline.cli",
            "prepare-data",
            "--data-root",
            str(workdir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "manifest" in completed.stdout.lower()
    assert (workdir / "manifest.csv").is_file()
    assert (workdir / "collection.json").is_file()
