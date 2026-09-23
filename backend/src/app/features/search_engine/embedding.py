from __future__ import annotations

import os
import threading
from collections.abc import Sequence

import httpx
import numpy as np

from app.core.errors import SearchServiceUnavailable


_encoder = None
_encoder_lock = threading.Lock()


class RemoteClipTextEncoder:
    def __init__(self) -> None:
        self.base_url = os.getenv(
            "KIS_EMBEDDING_URL",
            "http://localhost:9000",
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


def get_encoder() -> RemoteClipTextEncoder:
    global _encoder

    if _encoder is None:
        with _encoder_lock:
            if _encoder is None:
                _encoder = RemoteClipTextEncoder()

    return _encoder


def reset_encoder_cache() -> None:
    global _encoder

    with _encoder_lock:
        _encoder = None
