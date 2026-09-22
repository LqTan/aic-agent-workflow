from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

REQUIRED_COLUMNS = {
    "keyframe_id",
    "collection_id",
    "video_id",
    "frame_number",
    "timestamp_ms",
    "image_path",
    "video_path",
}


def build_manifest(
    data_root: Path | str,
    output_path: Path | str | None = None,
) -> dict:
    """Walk ``data_root/keyframes`` + ``map-keyframes`` and emit ``manifest.csv``.

    The manifest is the contract consumed by ``app.features.search_engine.builder``.
    Per video it joins:
      * ``map-keyframes/{video_id}.csv`` (n, frame_idx, pts_time) for ordering
      * ``clip-features-32/{video_id}.npy`` for vector index
      * ``keyframes/{video_id}/{n:03d}.jpg`` for the image reference
      * ``videos/{video_id}.mp4`` for the video reference
    """
    import csv as _csv

    data_root = Path(data_root).resolve()
    output_path = Path(output_path or data_root / "manifest.csv").resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "keyframe_id",
        "collection_id",
        "video_id",
        "keyframe_number",
        "clip_vector_index",
        "frame_number",
        "timestamp_ms",
        "image_path",
        "video_path",
    ]
    video_count = 0
    keyframe_count = 0
    with output_path.open("w", encoding="utf-8", newline="") as output:
        writer = _csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        keyframes_dir = data_root / "keyframes"
        for video_dir in sorted(keyframes_dir.iterdir()):
            if not video_dir.is_dir():
                continue
            video_id = video_dir.name
            map_file = data_root / "map-keyframes" / f"{video_id}.csv"
            clip_file = data_root / "clip-features-32" / f"{video_id}.npy"
            if not map_file.is_file() or not clip_file.is_file():
                raise ValueError(
                    f"{video_id}: thiếu map-keyframes hoặc clip-features-32"
                )
            video_count += 1
            with map_file.open("r", encoding="utf-8-sig", newline="") as mapping:
                reader = _csv.DictReader(mapping)
                required = {"n", "frame_idx", "pts_time"}
                if required - set(reader.fieldnames or []):
                    raise ValueError(
                        f"{map_file}: thiếu cột {sorted(required - set(reader.fieldnames or []))}"
                    )
                for vector_index, row in enumerate(reader):
                    keyframe_number = int(row["n"])
                    image = _resolve_image(video_dir, keyframe_number)
                    if image is None:
                        raise ValueError(
                            f"{video_id}: thiếu ảnh keyframe n={keyframe_number}"
                        )
                    video_file = data_root / "videos" / f"{video_id}.mp4"
                    writer.writerow(
                        {
                            "keyframe_id": f"{video_id}_{keyframe_number:06d}",
                            "collection_id": _collection_id(video_id),
                            "video_id": video_id,
                            "keyframe_number": keyframe_number,
                            "clip_vector_index": vector_index,
                            "frame_number": int(row["frame_idx"]),
                            "timestamp_ms": round(float(row["pts_time"]) * 1000),
                            "image_path": image.relative_to(data_root).as_posix(),
                            "video_path": (
                                video_file.relative_to(data_root).as_posix()
                                if video_file.is_file()
                                else ""
                            ),
                        }
                    )
                    keyframe_count += 1
    return {
        "videos": video_count,
        "keyframes": keyframe_count,
        "output": str(output_path),
    }


def validate_manifest(manifest_path: Path | str, data_root: Path | str | None = None) -> dict:
    """Sanity-check the produced manifest against the dataset on disk."""
    manifest_path = Path(manifest_path).resolve()
    data_root = Path(data_root or manifest_path.parent).resolve()
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    missing_columns = REQUIRED_COLUMNS - set(rows[0].keys() if rows else [])
    if missing_columns:
        raise ValueError(
            f"manifest thiếu cột: {', '.join(sorted(missing_columns))}"
        )

    duplicate_keyframes = [
        key for key, count in Counter(r["keyframe_id"] for r in rows).items() if count > 1
    ]
    duplicate_images = [
        key for key, count in Counter(r["image_path"] for r in rows).items() if count > 1
    ]
    missing_images: list[str] = []
    invalid_timestamps: list[str] = []
    invalid_frames: list[str] = []
    invalid_collections: list[str] = []

    for row in rows:
        image_path = data_root / row["image_path"]
        if not image_path.exists():
            missing_images.append(row["image_path"])
        try:
            if int(row["timestamp_ms"]) < 0:
                invalid_timestamps.append(row["keyframe_id"])
        except ValueError:
            invalid_timestamps.append(row["keyframe_id"])
        try:
            if int(row["frame_number"]) < 0:
                invalid_frames.append(row["keyframe_id"])
        except ValueError:
            invalid_frames.append(row["keyframe_id"])
        expected = row["video_id"].split("_V", 1)[0]
        if row["collection_id"] != expected:
            invalid_collections.append(row["keyframe_id"])

    video_ids = {r["video_id"] for r in rows}
    collection_ids = {r["collection_id"] for r in rows}
    failed = any(
        [
            duplicate_keyframes,
            duplicate_images,
            missing_images,
            invalid_timestamps,
            invalid_frames,
            invalid_collections,
        ]
    )
    return {
        "valid": not failed,
        "rows": len(rows),
        "videos": len(video_ids),
        "collections": len(collection_ids),
        "duplicate_keyframes": len(duplicate_keyframes),
        "duplicate_images": len(duplicate_images),
        "missing_images": len(missing_images),
        "invalid_timestamps": len(invalid_timestamps),
        "invalid_frames": len(invalid_frames),
        "invalid_collections": len(invalid_collections),
    }


def build_collection(manifest_path: Path | str, output_path: Path | str | None = None) -> dict:
    """Emit ``collection.json`` listing videos per collection."""
    import json

    manifest_path = Path(manifest_path).resolve()
    output_path = Path(
        output_path or manifest_path.with_name("collection.json")
    ).resolve()
    collections: dict[str, set[str]] = {}
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            collections.setdefault(row["collection_id"], set()).add(row["video_id"])
    payload = {
        "collections": [
            {"collection_id": key, "videos": sorted(value)}
            for key, value in sorted(collections.items())
        ]
    }
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return {"collections": len(collections), "output": str(output_path)}


def _resolve_image(video_dir: Path, keyframe_number: int) -> Path | None:
    extensions = (".jpg", ".jpeg", ".png")
    for width in (3, 4, 6):
        for extension in extensions:
            candidate = video_dir / f"{keyframe_number:0{width}d}{extension}"
            if candidate.is_file():
                return candidate
    return None


def _collection_id(video_id: str) -> str:
    if "_V" not in video_id:
        raise ValueError(f"video_id không đúng dạng Lxx_Vxxx: {video_id}")
    return video_id.split("_V", 1)[0]
