"""CLIP text encoder + local search server.

Single-process FastAPI app that:
- Exposes /embed for raw CLIP text embeddings (used by tools and tests).
- Exposes /api/search for hybrid text-to-keyframe search using a prebuilt
  Annoy / PCA / BoW index that ships next to the executable.
- Serves static frontend (Next.js `output: 'export'`) and dataset media
  (keyframes, videos) so the same binary can host the full UI + backend.
- Designed to be packaged with PyInstaller and wrapped by Electron.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from collections import Counter
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logger = logging.getLogger("clip-search")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def _resolve_base_dir() -> Path:
    """Return the directory that contains models/ + data/ + frontend/ assets.

    PyInstaller --onedir sets _MEIPASS to the bundle's _internal/ directory
    where --add-data assets are placed. In dev (uv run) we fall back to the
    script directory. PyInstaller --onefile uses a temp dir at runtime.
    """
    meipass = getattr(os, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return Path(__file__).resolve().parent


BASE_DIR = _resolve_base_dir()
MODEL_PATH = BASE_DIR / "models" / "text_encoder.onnx"
TOKENIZER_PATH = BASE_DIR / "models" / "tokenizer"
DATA_ROOT = Path(os.getenv("DATA_ROOT", BASE_DIR / "data")).resolve()
INDEX_ROOT = Path(os.getenv("INDEX_ROOT", DATA_ROOT / "search_index")).resolve()
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", BASE_DIR / "frontend")).resolve()

INDEX_FORMAT_VERSION = 2


class _SearchIndex:
    """Loads the prebuilt search index once and caches it process-wide."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._loaded = False
        self.metadata: dict = {}
        self.full_vectors: np.ndarray | None = None
        self.reduced: np.ndarray | None = None
        self.pca_components: np.ndarray | None = None
        self.pca_mean: np.ndarray | None = None
        self.records: list[dict] = []
        self.trees: dict[str, object] = {}
        self.trees_format: dict[str, str] = {}

    def load(self) -> None:
        with self._lock:
            if self._loaded:
                return
            metadata_path = INDEX_ROOT / "metadata.json"
            if not metadata_path.is_file():
                raise RuntimeError(
                    f"Search index not found at {INDEX_ROOT}. "
                    "Set INDEX_ROOT or place data/search_index/ next to the exe."
                )
            with metadata_path.open("r", encoding="utf-8") as handle:
                self.metadata = json.load(handle)
            if self.metadata.get("format_version") != INDEX_FORMAT_VERSION:
                raise RuntimeError(
                    "Search index version mismatch; rebuild via backend pipeline."
                )

            self.full_vectors = np.load(INDEX_ROOT / "full_vectors.npy", mmap_mode="r")
            self.reduced = np.load(INDEX_ROOT / "reduced.npy")
            self.pca_components = np.load(INDEX_ROOT / "pca_components.npy")
            self.pca_mean = np.load(INDEX_ROOT / "pca_mean.npy")

            with (INDEX_ROOT / "records.jsonl").open("r", encoding="utf-8") as handle:
                self.records = [json.loads(line) for line in handle if line.strip()]

            self.trees_format = self.metadata.get("tree_files", {})
            self._loaded = True
            logger.info(
                "Search index loaded: %d records, %d trees",
                len(self.records),
                len(self.trees_format),
            )

    def reduce_query(self, vector: np.ndarray) -> np.ndarray:
        if self.pca_components is None or self.pca_mean is None:
            raise RuntimeError("Index not loaded")
        query = np.asarray(vector, dtype=np.float32).reshape(-1)
        if query.shape[0] != self.full_vectors.shape[1]:
            raise ValueError(
                f"Query vector has {query.shape[0]} dims, index needs "
                f"{self.full_vectors.shape[1]}"
            )
        return ((query - self.pca_mean) @ self.pca_components.T).astype(np.float32)


_index = _SearchIndex()
_ort_session: ort.InferenceSession | None = None
_tokenizer = None
_tokenizer_lock = threading.Lock()


def _load_runtime() -> None:
    global _ort_session, _tokenizer
    if _ort_session is not None and _tokenizer is not None:
        return
    with _tokenizer_lock:
        if _ort_session is not None and _tokenizer is not None:
            return
        if not MODEL_PATH.is_file():
            raise RuntimeError(f"ONNX model not found at {MODEL_PATH}")
        _ort_session = ort.InferenceSession(
            str(MODEL_PATH),
            providers=["CPUExecutionProvider"],
        )
        from transformers import CLIPTokenizerFast

        _tokenizer = CLIPTokenizerFast.from_pretrained(
            TOKENIZER_PATH,
            local_files_only=True,
        )
        logger.info("CLIP runtime loaded from %s", MODEL_PATH)


def _encode_texts(texts: list[str]) -> np.ndarray:
    """Encode one or more texts to CLIP embeddings.

    The exported ONNX model is fixed-batch=1 (a known limitation of the
    PyTorch export used in this project). We encode each text individually
    so callers can pass arbitrary-length lists.
    """
    _load_runtime()
    if len(texts) == 1:
        tokens = _tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=77,
            return_tensors="np",
        )["input_ids"].astype(np.int64)
        embeddings = _ort_session.run(
            ["clip_text_output"],
            {"tokens": tokens},
        )[0]
        return np.asarray(embeddings, dtype=np.float32)

    per_text = []
    for text in texts:
        tokens = _tokenizer(
            [text],
            padding="max_length",
            truncation=True,
            max_length=77,
            return_tensors="np",
        )["input_ids"].astype(np.int64)
        embedding = _ort_session.run(
            ["clip_text_output"],
            {"tokens": tokens},
        )[0]
        per_text.append(np.asarray(embedding, dtype=np.float32))
    return np.concatenate(per_text, axis=0)


def _search_local(query_embedding: np.ndarray, top_k: int) -> list[dict]:
    """Brute-force cosine over PCA-reduced vectors.

    Good enough for ~10k records; we keep it dependency-free (no annoy).
    """
    _index.load()
    reduced_query = _index.reduce_query(query_embedding)
    reduced = _index.reduced
    norms = np.linalg.norm(reduced, axis=1)
    q_norm = float(np.linalg.norm(reduced_query))
    if q_norm == 0.0:
        return []
    scores = (reduced @ reduced_query) / (norms * q_norm + 1e-12)
    top_idx = np.argsort(-scores)[:top_k]

    results: list[dict] = []
    for rank, idx in enumerate(top_idx, start=1):
        rec = _index.records[int(idx)]
        score = float(scores[int(idx)])
        image_rel = rec.get("image_path", "")
        video_rel = rec.get("video_path", "")
        results.append({
            "rank": rank,
            "keyframe_id": rec.get("keyframe_id", ""),
            "collection_id": rec.get("collection_id", ""),
            "video_id": rec.get("video_id", ""),
            "frame_number": int(rec.get("frame_number", 0)),
            "frame_id": int(rec.get("keyframe_number", 0)),
            "timestamp_ms": int(rec.get("timestamp_ms", 0)),
            "image_path": image_rel,
            "video_path": video_rel,
            "image_url": f"/static/{image_rel}" if image_rel else "",
            "video_url": f"/static/{video_rel}" if video_rel else "",
            "score": score,
        })
    return results


# ---------------------------------------------------------------------------
# Search history store (in-memory, lost on restart)
# ---------------------------------------------------------------------------


QUALITY_THRESHOLD = 0.5


class SearchHistoryStore:
    """Thread-safe ring buffer of recent search runs.

    Drives the dashboard, history, analysis, and evaluation endpoints so
    they all see real activity instead of mocks.
    """

    def __init__(self, max_size: int = 200) -> None:
        self._max_size = max_size
        self._lock = threading.Lock()
        self._runs: list[dict] = []

    def record(
        self,
        query: str,
        results: list[dict],
        duration_ms: int,
    ) -> dict:
        run_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc)
        top_score = results[0]["score"] if results else 0.0
        collection_ids = sorted({
            r.get("collection_id", "") for r in results if r.get("collection_id")
        })
        entry = {
            "run_id": run_id,
            "goal": query,
            "query": query,
            "timestamp": now.isoformat(),
            "timestamp_ms": int(now.timestamp() * 1000),
            "results": results,
            "top_score": top_score,
            "duration_ms": duration_ms,
            "decision": "accepted" if top_score >= QUALITY_THRESHOLD else "best_effort",
            "collection_ids": collection_ids,
        }
        with self._lock:
            self._runs.insert(0, entry)
            if len(self._runs) > self._max_size:
                self._runs = self._runs[: self._max_size]
        return entry

    def list(self, limit: int = 100) -> list[dict]:
        with self._lock:
            return list(self._runs[:limit])

    def get(self, run_id: str) -> dict | None:
        with self._lock:
            for r in self._runs:
                if r["run_id"] == run_id:
                    return r
        return None


_history = SearchHistoryStore()


def _wrap_search_response(entry: dict) -> dict:
    """Convert a stored history entry into the VideoSearchResponse shape
    that the frontend's analysis detail page expects."""
    results = entry["results"]
    return {
        "goal": entry["query"],
        "plan": {
            "intent": entry["query"],
            "original_query": entry["query"],
            "search_query": entry["query"],
            "objects": [],
            "actions": [],
            "scenes": [],
            "collection_ids": entry["collection_ids"],
            "planner": "local-clip",
        },
        "attempts": [
            {
                "attempt": 1,
                "query": entry["query"],
                "result_count": len(results),
                "quality_score": entry["top_score"],
                "threshold": QUALITY_THRESHOLD,
                "accepted": entry["top_score"] >= QUALITY_THRESHOLD,
            },
        ],
        "trace": [
            {
                "step": "local-search",
                "status": "completed",
                "detail": {"count": len(results), "query": entry["query"]},
            },
        ],
        "decision": entry["decision"],
        "quality_score": entry["top_score"],
        "count": len(results),
        "results": results,
    }


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        _load_runtime()
    except Exception as exc:
        logger.warning("CLIP runtime failed to preload: %s", exc)
    try:
        _index.load()
    except Exception as exc:
        logger.warning("Search index failed to preload: %s", exc)
    yield


app = FastAPI(title="CLIP Local Search", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmbedRequest(BaseModel):
    texts: list[str]


class SearchRequest(BaseModel):
    query: str
    top_k: int = 12


@app.get("/health")
def health():
    return {
        "status": "ok",
        "data_root": str(DATA_ROOT),
        "index_root": str(INDEX_ROOT),
        "frontend_dist": str(FRONTEND_DIST),
        "index_loaded": _index._loaded,
        "runtime_loaded": _ort_session is not None,
    }


@app.post("/embed")
def embed(body: EmbedRequest):
    if not body.texts:
        raise HTTPException(status_code=400, detail="texts is empty")
    vectors = _encode_texts(body.texts)
    return {"embeddings": vectors.tolist()}


@app.post("/api/search")
def search(body: SearchRequest):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="query is empty")
    try:
        started = time.perf_counter()
        vector = _encode_texts([body.query])[0]
        results = _search_local(vector, top_k=max(1, min(body.top_k, 50)))
        duration_ms = int((time.perf_counter() - started) * 1000)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    entry = _history.record(body.query, results, duration_ms)

    return {
        "query": body.query,
        "count": len(results),
        "results": results,
        "run_id": entry["run_id"],
        "duration_ms": duration_ms,
    }


# ---------------------------------------------------------------------------
# Dashboard / history / analysis / evaluation endpoints
# ---------------------------------------------------------------------------


def _search_run_summary(entry: dict) -> dict:
    """Compact view of a history entry used by multiple endpoints."""
    return {
        "id": entry["run_id"],
        "goal": entry["goal"],
        "query": entry["query"],
        "timestamp": entry["timestamp"],
        "qualityScore": entry["top_score"],
        "attempts": 1,
        "decision": entry["decision"],
        "resultCount": len(entry["results"]),
        "durationMs": entry["duration_ms"],
        "collectionIds": entry["collection_ids"],
        "planner": "local-clip",
    }


@app.get("/api/dashboard/overview")
def dashboard_overview():
    _index.load()
    history = _history.list(limit=200)
    video_ids = {r.get("video_id", "") for r in _index.records if r.get("video_id")}
    collection_ids = {
        r.get("collection_id", "") for r in _index.records if r.get("collection_id")
    }

    total = len(history)
    accepted = sum(1 for h in history if h["decision"] == "accepted")
    avg_quality = (
        sum(h["top_score"] for h in history) / total if total else 0.0
    )
    avg_duration = (
        sum(h["duration_ms"] for h in history) / total if total else 0
    )

    recent_runs = [_search_run_summary(h) for h in history[:5]]

    # Per-collection breakdown, useful as a quality trend placeholder.
    quality_trend: list[dict] = []
    if history:
        bucket_count = 6
        per_bucket = max(1, len(history) // bucket_count)
        for i in range(bucket_count):
            slice_ = history[i * per_bucket : (i + 1) * per_bucket]
            if not slice_:
                continue
            avg = sum(h["top_score"] for h in slice_) / len(slice_)
            quality_trend.append({
                "date": slice_[0]["timestamp"][:10],
                "averageQualityScore": round(avg, 4),
                "queryCount": len(slice_),
            })

    return {
        "totalQueries": total,
        "acceptedQueries": accepted,
        "bestEffortQueries": total - accepted,
        "averageQualityScore": round(avg_quality, 4),
        "averageAttempts": 1.0,
        "averageDurationMs": int(avg_duration),
        "totalIndexedVideos": len(video_ids),
        "totalCollections": len(collection_ids),
        "lastUpdatedAt": datetime.now(timezone.utc).isoformat(),
        "recentRuns": recent_runs,
        "qualityTrend": quality_trend,
    }


@app.get("/api/history/")
def history_list(
    decision: str | None = None,
    query: str | None = None,
    limit: int = 100,
):
    history = _history.list(limit=limit)
    entries: list[dict] = []
    for h in history:
        if decision and decision != "all":
            if decision == "accepted" and h["decision"] != "accepted":
                continue
            if decision == "best_effort" and h["decision"] != "best_effort":
                continue
        if query and query.lower() not in h["query"].lower():
            continue
        entries.append(_search_run_summary(h))
    return {"total": len(entries), "entries": entries}


@app.get("/api/analysis/runs")
def analysis_runs():
    history = _history.list(limit=200)
    runs = [_search_run_summary(h) for h in history]
    return {"total": len(runs), "runs": runs}


@app.get("/api/analysis/runs/{run_id}")
def analysis_run(run_id: str):
    entry = _history.get(run_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="run not found")
    return _wrap_search_response(entry)


@app.get("/api/evaluation/overview")
def evaluation_overview():
    history = _history.list(limit=200)
    total = len(history)
    scores = [h["top_score"] for h in history]
    avg_quality = sum(scores) / total if total else 0.0
    avg_latency = (
        sum(h["duration_ms"] for h in history) / total if total else 0
    )

    buckets = [
        {"bucket": "< 0.3", "min": 0.0, "max": 0.3, "count": 0},
        {"bucket": "0.3 - 0.5", "min": 0.3, "max": 0.5, "count": 0},
        {"bucket": "0.5 - 0.7", "min": 0.5, "max": 0.7, "count": 0},
        {"bucket": ">= 0.7", "min": 0.7, "max": 1.01, "count": 0},
    ]
    for s in scores:
        for b in buckets:
            if b["min"] <= s < b["max"]:
                b["count"] += 1
                break

    accepted = sum(1 for s in scores if s >= QUALITY_THRESHOLD)

    runs = []
    for h in history[:20]:
        runs.append({
            "id": h["run_id"],
            "goal": h["goal"],
            "query": h["query"],
            "timestamp": h["timestamp"],
            "qualityScore": h["top_score"],
            "threshold": QUALITY_THRESHOLD,
            "attempts": 1,
            "decision": h["decision"],
            "resultCount": len(h["results"]),
            "latencyMs": h["duration_ms"],
            "collectionIds": h["collection_ids"],
        })

    return {
        "totalRuns": total,
        "averageQuality": round(avg_quality, 4),
        "averageAttempts": 1.0,
        "averageLatency": int(avg_latency),
        "thresholdDefault": QUALITY_THRESHOLD,
        "decisionDistribution": {
            "accepted": accepted,
            "bestEffort": total - accepted,
        },
        "qualityDistribution": buckets,
        "runs": runs,
    }


@app.get("/static/{path:path}")
def static_file(path: str):
    """Serve dataset media (keyframes + videos) from DATA_ROOT.

    Path traversal is blocked by resolving the requested path and ensuring
    it stays under DATA_ROOT.
    """
    requested = (DATA_ROOT / path).resolve()
    try:
        requested.relative_to(DATA_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="not found") from exc
    if not requested.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(str(requested))


# Serve built frontend (Next.js `output: 'export'`) at root.
# Must be registered last because it catches every unmatched path.
if FRONTEND_DIST.is_dir():
    frontend_root = FRONTEND_DIST

    @app.get("/{path:path}")
    def frontend_spa(path: str):
        """Serve the static-export frontend.

        Next.js emits files like /search.html for each route. Browsers hit
        /search (no extension), so we resolve the .html file ourselves
        before falling back to static-asset lookup. Anything that looks
        like an API or static-data path returns 404 instead of HTML so
        clients can distinguish missing endpoints from missing routes.
        """
        if path.startswith(("api/", "static/")):
            raise HTTPException(status_code=404, detail="not found")
        # Serve /_next/* static assets directly from the export dir.
        if path.startswith("_next/"):
            asset = (frontend_root / path).resolve()
            try:
                asset.relative_to(frontend_root)
            except ValueError:
                raise HTTPException(status_code=404, detail="not found")
            if asset.is_file():
                return FileResponse(str(asset))
            raise HTTPException(status_code=404, detail="not found")
        candidate = (frontend_root / path).resolve()
        try:
            candidate.relative_to(frontend_root)
        except ValueError:
            raise HTTPException(status_code=404, detail="not found")
        if candidate.is_file():
            return FileResponse(str(candidate))
        if candidate.is_dir() and (candidate / "index.html").is_file():
            return FileResponse(str(candidate / "index.html"))
        html_candidate = frontend_root / f"{path}.html"
        if html_candidate.is_file():
            return FileResponse(str(html_candidate))
        index_html = frontend_root / "index.html"
        if index_html.is_file():
            return FileResponse(str(index_html))
        raise HTTPException(status_code=404, detail="not found")
else:
    @app.get("/")
    def root_fallback():
        return JSONResponse(
            {
                "name": "clip-search",
                "frontend_dist": str(FRONTEND_DIST),
                "hint": "Build frontend with `NEXT_OUTPUT=export npm run build` "
                "and place output under frontend/ next to this exe.",
            }
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "9000")),
    )
