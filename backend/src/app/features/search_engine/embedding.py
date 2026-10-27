from __future__ import annotations

import logging
import os
import threading
from collections.abc import Sequence
from pathlib import Path

import httpx
import numpy as np

from app.core.errors import SearchServiceUnavailable

logger = logging.getLogger(__name__)

_encoder = None
_encoder_lock = threading.Lock()


class LocalOnnxClipEncoder:
    """In-process CLIP text encoder using ONNX Runtime and HuggingFace CLIPTokenizerFast."""

    def __init__(self, model_path: Path | str, tokenizer_path: Path | str) -> None:
        self.model_path = Path(model_path).resolve()
        self.tokenizer_path = Path(tokenizer_path).resolve()
        self._session = None
        self._tokenizer = None
        self._load_lock = threading.Lock()

    def _ensure_loaded(self) -> None:
        if self._session is not None and self._tokenizer is not None:
            return
        with self._load_lock:
            if self._session is not None and self._tokenizer is not None:
                return

            if not self.model_path.is_file():
                raise SearchServiceUnavailable(
                    f"Không tìm thấy ONNX text encoder model tại {self.model_path}."
                )
            if not self.tokenizer_path.is_dir():
                raise SearchServiceUnavailable(
                    f"Không tìm thấy tokenizer tại {self.tokenizer_path}."
                )

            try:
                import onnxruntime as ort
                from transformers import CLIPTokenizerFast
            except ImportError as exc:
                raise SearchServiceUnavailable(
                    f"Thiếu thư viện onnxruntime hoặc transformers ({exc}). Chạy: uv sync"
                ) from exc

            opts = ort.SessionOptions()
            opts.intra_op_num_threads = min(4, os.cpu_count() or 1)
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self._session = ort.InferenceSession(
                str(self.model_path),
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
            self._tokenizer = CLIPTokenizerFast.from_pretrained(
                str(self.tokenizer_path),
                local_files_only=True,
            )
            logger.info("Local ONNX CLIP encoder loaded from %s", self.model_path)

    def encode_text(self, text: str) -> np.ndarray:
        return self.encode_texts([text])[0]

    def encode_texts(
        self,
        texts: Sequence[str],
        batch_size: int = 64,
    ) -> np.ndarray:
        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        self._ensure_loaded()
        assert self._tokenizer is not None
        assert self._session is not None

        embeddings = []
        for text in texts:
            tokens = self._tokenizer(
                [text],
                padding="max_length",
                truncation=True,
                max_length=77,
                return_tensors="np",
            )["input_ids"].astype(np.int64)

            emb = self._session.run(
                ["clip_text_output"],
                {"tokens": tokens},
            )[0]
            embeddings.append(np.asarray(emb[0], dtype=np.float32))

        return np.asarray(embeddings, dtype=np.float32)


class RemoteClipTextEncoder:
    """HTTP client for a remote CLIP embedding server."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (
            base_url or os.getenv("KIS_EMBEDDING_URL", "http://localhost:9000")
        ).rstrip("/")

    def encode_text(self, text: str) -> np.ndarray:
        return self.encode_texts([text])[0]

    def encode_texts(
        self,
        texts: Sequence[str],
        batch_size: int = 64,
    ) -> np.ndarray:
        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        try:
            response = httpx.post(
                f"{self.base_url}/embed",
                json={"texts": list(texts)},
                timeout=30.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SearchServiceUnavailable(
                f"ONNX embedding server unavailable: {exc}"
            ) from exc

        data = response.json()
        return np.asarray(
            data["embeddings"],
            dtype=np.float32,
        )


def get_encoder() -> LocalOnnxClipEncoder | RemoteClipTextEncoder:
    global _encoder

    if _encoder is None:
        with _encoder_lock:
            if _encoder is None:
                from app.core.config import get_settings

                settings = get_settings()
                provider = (settings.kis_embedding_provider or "").lower().strip()

                if provider == "remote" and settings.kis_embedding_url:
                    _encoder = RemoteClipTextEncoder(settings.kis_embedding_url)
                else:
                    model_path = settings.resolved_onnx_model_path()
                    tok_path = settings.resolved_tokenizer_path()
                    if model_path.is_file() and tok_path.is_dir():
                        _encoder = LocalOnnxClipEncoder(model_path, tok_path)
                    elif settings.kis_embedding_url:
                        _encoder = RemoteClipTextEncoder(settings.kis_embedding_url)
                    else:
                        _encoder = LocalOnnxClipEncoder(model_path, tok_path)

    return _encoder


def reset_encoder_cache() -> None:
    global _encoder

    with _encoder_lock:
        _encoder = None
