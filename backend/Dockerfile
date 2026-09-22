FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

# Pre-install uv + deps in a cached layer. The `[hybrid]` extra pulls in
# `torch` + `open-clip-torch` so the real search index can run inside the
# container. If you run in demo mode set `KIS_DEMO_MODE=true` instead and
# the heavy deps stay on disk but unused.
COPY pyproject.toml uv.lock* ./
RUN pip install uv \
    && uv sync --no-dev --extra hybrid --frozen \
    || uv sync --no-dev --extra hybrid

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
