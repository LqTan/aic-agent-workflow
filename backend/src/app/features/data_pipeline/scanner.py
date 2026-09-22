from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")
REQUIRED_SOURCES = (
    "keyframes",
    "map-keyframes",
    "objects",
    "videos",
    "clip-features-32",
)


@dataclass(frozen=True)
class DatasetReport:
    data_root: str
    source_video_counts: dict[str, int]
    collections: dict[str, int]
    common_video_count: int
    missing_by_source: dict[str, list[str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors and not any(self.missing_by_source.values())

    def to_dict(self) -> dict:
        result = asdict(self)
        result["valid"] = self.valid
        return result


def scan_dataset(data_root: Path | str, *, deep: bool = False) -> DatasetReport:
    data_root = Path(data_root).resolve()
    sources = {
        "keyframes": _directory_ids(data_root / "keyframes"),
        "map-keyframes": _file_ids(data_root / "map-keyframes", ".csv"),
        "objects": _directory_ids(data_root / "objects"),
        "videos": _file_ids(data_root / "videos", ".mp4"),
        "clip-features-32": _file_ids(data_root / "clip-features-32", ".npy"),
    }
    errors = [
        f"Thiếu thư mục: {data_root / source}"
        for source in REQUIRED_SOURCES
        if not (data_root / source).is_dir()
    ]
    all_ids = set().union(*sources.values()) if sources else set()
    missing = {
        source: sorted(all_ids - video_ids)
        for source, video_ids in sources.items()
        if all_ids - video_ids
    }
    collections = Counter(_collection_id(video_id) for video_id in all_ids)
    common = (
        set.intersection(*sources.values())
        if sources and all(sources.values())
        else set()
    )
    if not all_ids:
        errors.append("Không tìm thấy video_id nào trong data-root")
    elif not common:
        errors.append("Không có video_id nào xuất hiện đầy đủ ở mọi nguồn bắt buộc")

    if deep:
        for video_id in sorted(common):
            errors.extend(_validate_video(data_root, video_id))

    return DatasetReport(
        data_root=str(data_root),
        source_video_counts={key: len(value) for key, value in sources.items()},
        collections=dict(sorted(collections.items())),
        common_video_count=len(common),
        missing_by_source=missing,
        errors=errors,
    )


def _validate_video(data_root: Path, video_id: str) -> list[str]:
    import numpy as np

    errors: list[str] = []
    images = [
        path
        for path in (data_root / "keyframes" / video_id).iterdir()
        if path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    mapping_path = data_root / "map-keyframes" / f"{video_id}.csv"
    if not mapping_path.is_file():
        return [f"{video_id}: thiếu map-keyframes"]
    with mapping_path.open("r", encoding="utf-8-sig", newline="") as handle:
        mapping = list(__import__("csv").DictReader(handle))
    feature_path = data_root / "clip-features-32" / f"{video_id}.npy"
    if feature_path.is_file():
        features = np.load(feature_path, mmap_mode="r")
        feature_count = features.shape[0] if features.ndim == 2 else -1
    else:
        feature_count = -1
    if len(images) != len(mapping) or (
        feature_count >= 0 and len(mapping) != feature_count
    ):
        errors.append(
            f"{video_id}: keyframes={len(images)}, map={len(mapping)}, clip={feature_count}"
        )
    expected = [int(row["n"]) for row in mapping]
    actual = sorted(int(path.stem) for path in images if path.stem.isdigit())
    if expected != actual:
        errors.append(f"{video_id}: tên ảnh không khớp cột n trong map-keyframes")
    return errors


def _directory_ids(path: Path) -> set[str]:
    return {item.name for item in path.iterdir() if item.is_dir()} if path.is_dir() else set()


def _file_ids(path: Path, suffix: str) -> set[str]:
    return (
        {item.stem for item in path.glob(f"*{suffix}")} if path.is_dir() else set()
    )


def _collection_id(video_id: str) -> str:
    if "_V" not in video_id:
        raise ValueError(f"video_id không đúng dạng Lxx_Vxxx: {video_id}")
    return video_id.split("_V", 1)[0]
