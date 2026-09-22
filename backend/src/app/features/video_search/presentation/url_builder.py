from __future__ import annotations

from pathlib import Path

from fastapi import Request

ALLOWED_ASSET_FOLDERS = {"keyframes", "videos"}


def normalize_asset_path(asset_path: str) -> Path | None:
    """Reject path traversal and restrict to keyframes/ or videos/."""
    relative = Path(asset_path.replace("\\", "/"))
    if (
        not relative.parts
        or ".." in relative.parts
        or relative.parts[0] not in ALLOWED_ASSET_FOLDERS
    ):
        return None
    return relative


def build_asset_url(request: Request, relative_path: str) -> str:
    return str(request.url_for("dataset_asset", asset_path=relative_path))


def format_results_with_urls(*, results: list[dict], request: Request, data_root: Path) -> list[dict]:
    """Add image_url/video_url fields and forward-compatible keyframe_id mapping."""
    enriched: list[dict] = []
    for item in results:
        new = dict(item)
        image_path = (new.get("image_path") or "").strip().replace("\\", "/").lstrip("/")
        video_path = (new.get("video_path") or "").strip().replace("\\", "/").lstrip("/")
        if image_path:
            new["image_url"] = build_asset_url(request, image_path)
        if not video_path:
            video_path = f"videos/{new.get('video_id')}.mp4"
        new["video_path"] = video_path
        new["video_url"] = build_asset_url(request, video_path)
        new["frame_id"] = new.get("frame_id", new.get("frame_number", 0))
        enriched.append(new)
    return enriched
