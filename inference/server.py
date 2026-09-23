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
from contextlib import asynccontextmanager
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
        vector = _encode_texts([body.query])[0]
        results = _search_local(vector, top_k=max(1, min(body.top_k, 50)))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "query": body.query,
        "count": len(results),
        "results": results,
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
