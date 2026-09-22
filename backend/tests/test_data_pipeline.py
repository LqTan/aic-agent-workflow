from __future__ import annotations

import csv
import shutil
from pathlib import Path

import pytest

from app.features.data_pipeline.manifest import (
    build_collection,
    build_manifest,
    validate_manifest,
)
from app.features.data_pipeline.scanner import scan_dataset

# Skip the entire module if the dataset is not present locally.
# CI runs without `../data` so these tests are opt-in by file existence.
DATASET_ROOT = Path(__file__).resolve().parents[2] / "data"


pytestmark = pytest.mark.skipif(
    not DATASET_ROOT.is_dir(),
    reason=f"AIC dataset not found at {DATASET_ROOT}; skipping real-data tests.",
)


@pytest.fixture(scope="module")
def workdir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Copy the dataset into a tmpdir to avoid touching the host manifest."""
    workdir = tmp_path_factory.mktemp("data_pipeline")
    for sub in ("keyframes", "map-keyframes", "objects", "videos", "clip-features-32"):
        src = DATASET_ROOT / sub
        if src.is_dir():
            shutil.copytree(src, workdir / sub)
    return workdir


def test_scanner_reports_common_videos(workdir: Path) -> None:
    report = scan_dataset(workdir)
    assert report.common_video_count > 0
    assert "L21" in report.collections or any(
        coll.startswith("L") for coll in report.collections
    )
    # Per-source counts must all be > 0.
    for source, count in report.source_video_counts.items():
        assert count > 0, f"source {source} has 0 videos"


def test_build_manifest_writes_csv(workdir: Path) -> None:
    info = build_manifest(workdir)
    assert info["videos"] > 0
    assert info["keyframes"] > 0
    manifest_path = Path(info["output"])
    assert manifest_path.is_file()

    with manifest_path.open(encoding="utf-8") as handle:
        header = next(csv.reader(handle))
    for required in (
        "keyframe_id",
        "collection_id",
        "video_id",
        "keyframe_number",
        "clip_vector_index",
        "frame_number",
        "timestamp_ms",
        "image_path",
        "video_path",
    ):
        assert required in header


def test_validate_manifest_passes(workdir: Path) -> None:
    info = build_manifest(workdir)
    result = validate_manifest(info["output"], data_root=workdir)
    assert result["valid"] is True
    assert result["rows"] == info["keyframes"]
    assert result["missing_images"] == 0
    assert result["duplicate_keyframes"] == 0


def test_build_collection_aggregates_by_collection(workdir: Path) -> None:
    info = build_manifest(workdir)
    summary = build_collection(info["output"])
    assert summary["collections"] > 0
    assert Path(summary["output"]).is_file()
