from __future__ import annotations

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.features.search_engine.embedding import (
    LocalOnnxClipEncoder,
    get_encoder,
    reset_encoder_cache,
)
from app.main import app


def test_encoder_initialization():
    settings = get_settings()
    model_path = settings.resolved_onnx_model_path()
    tok_path = settings.resolved_tokenizer_path()

    if not model_path.is_file() or not tok_path.is_dir():
        pytest.skip(f"ONNX model or tokenizer not found ({model_path}, {tok_path})")

    encoder = LocalOnnxClipEncoder(model_path, tok_path)
    assert encoder.model_path == model_path
    assert encoder.tokenizer_path == tok_path


def test_embed_api_endpoint():
    client = TestClient(app)
    # Test validation error on empty texts
    res = client.post("/embed", json={"texts": []})
    assert res.status_code == 400

    res2 = client.post("/api/v1/embed", json={"texts": "invalid"})
    assert res2.status_code == 400

