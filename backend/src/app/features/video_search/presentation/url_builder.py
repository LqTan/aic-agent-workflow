from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from fastapi import Request

ALLOWED_ASSET_FOLDERS = {"keyframes", "videos"}
DEFAULT_ASSET_PATH = "/api/v1/kis/assets"


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


def _join(base_url: str, asset_path: str) -> str:
    """Build a stable absolute URL out of a base + relative path."""
    return urljoin(base_url.rstrip("/") + "/", asset_path.lstrip("/"))


def build_asset_url_from_request(request: Request, relative_path: str) -> str:
    return str(request.url_for("dataset_asset", asset_path=relative_path))


def build_asset_url_from_base(base_url: str, relative_path: str) -> str:
    return f"{base_url.rstrip('/')}/{DEFAULT_ASSET_PATH}/{relative_path.lstrip('/')}"


def format_results_with_urls(
    *,
    results: list[dict],
    source: Request | str,
) -> list[dict]:
    """Enrich results with ``image_url`` and ``video_url`` for the client.

    ``source`` is either a FastAPI ``Request`` (HTTP API) or a base URL string
    used by tools / n8n workflows.
    """
    enriched: list[dict] = []
    for item in results:
        new = dict(item)
        image_path = (new.get("image_path") or "").strip().replace("\\", "/").lstrip("/")
        video_path = (new.get("video_path") or "").strip().replace("\\", "/").lstrip("/")
        if image_path:
            if isinstance(source, Request):
                new["image_url"] = build_asset_url_from_request(source, image_path)
            else:
                new["image_url"] = build_asset_url_from_base(source, image_path)
        if not video_path:
            video_path = f"videos/{new.get('video_id')}.mp4"
        new["video_path"] = video_path
        if isinstance(source, Request):
            new["video_url"] = build_asset_url_from_request(source, video_path)
        else:
            new["video_url"] = build_asset_url_from_base(source, video_path)
        new["frame_id"] = new.get("frame_id", new.get("frame_number", 0))
        enriched.append(new)
    return enriched
