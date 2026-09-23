from pathlib import Path

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import CLIPTokenizerFast


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "text_encoder.onnx"
TOKENIZER_PATH = BASE_DIR / "models" / "tokenizer"

app = FastAPI()

session = ort.InferenceSession(
    str(MODEL_PATH),
    providers=["CPUExecutionProvider"],
)

tokenizer = CLIPTokenizerFast.from_pretrained(
    TOKENIZER_PATH,
    local_files_only=True,
)


class EmbedRequest(BaseModel):
    texts: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/embed")
def embed(body: EmbedRequest):
    tokens = tokenizer(
        body.texts,
        padding="max_length",
        truncation=True,
        max_length=77,
        return_tensors="np",
    )["input_ids"].astype(np.int64)

    embeddings = session.run(
        ["clip_text_output"],
        {"tokens": tokens},
    )[0]

    return {
        "embeddings": embeddings.tolist()
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
    )
