# AIC Video Retrieval Platform

Hệ thống tìm kiếm video/keyframe hybrid (`domain routing + object bag-of-words + PCA/R-tree + exact CLIP rerank`) với lớp **Agentic AI**: phân tích truy vấn tiếng Việt, lập kế hoạch, gọi search tool, tự đánh giá Top-K và viết lại truy vấn để tìm lại.

Repo có **hai source song song**:

| Thư mục | Trạng thái | Stack |
|---|---|---|
| `backend/` + `frontend/` | **Source chính, đang phát triển** | FastAPI (Python 3.12) + Next.js 16 |
| `BE/` + `FE/` | Bản Django/React cũ, giữ để tham chiếu | Django 5 + React + Vite |
| `electron/` | Shell desktop demo, build `.exe` portable | Electron + PyInstaller |

Hướng dẫn dưới đây chỉ dành cho source chính `backend/` + `frontend/`.

## Chạy dev nhanh (2 terminal)

**Terminal 1 — Backend** (`http://localhost:8000`):

```bash
cd backend
uv sync --extra dev
cp .env.example .env
uv run aic-dev          # tương đương: uvicorn app.main:app --reload
```

**Terminal 2 — Frontend** (`http://localhost:3000`):

```bash
cd frontend
npm install
cp .env.local .env.local.template 2>/dev/null || true
npm run dev
```

Đảm bảo `frontend/.env.local` có:

```env
NEXT_PUBLIC_USE_MOCKS=false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

Tắt nhanh backend đang chạy: `backend/scripts/kill_app.sh`.

## Yêu cầu

- Python 3.12, [uv](https://docs.astral.sh/uv/) (`pip install uv` hoặc cài qua Astral)
- Node.js ≥ 24, npm ≥ 11
- (Tuỳ chọn) Docker Compose v2 để chạy PostgreSQL + Redis cho dev

## Cấu trúc source chính

```text
backend/
├── pyproject.toml          # uv project, scripts: aic-dev, aic-prepare-data, aic-build-index, aic-lint, aic-test
├── alembic/                # migration khi cần version hoá schema
├── src/app/
│   ├── core/               # Settings, errors, logging
│   ├── shared/db/          # SQLModel engine
│   ├── features/
│   │   ├── video_search/   # KIS hybrid + agent (router: /kis, /kis/tools)
│   │   ├── search_run/     # Lưu lịch sử agent run
│   │   ├── dashboard/      # Tổng quan
│   │   ├── history/        # Lịch sử truy vấn
│   │   ├── analysis/       # Phân tích kết quả
│   │   ├── evaluation/     # Đánh giá chất lượng
│   │   ├── data_pipeline/  # Scan + manifest + collection
│   │   └── search_engine/  # BoW, PCA, R-tree, reranker
│   └── main.py             # FastAPI app, prefix /api/v1
├── tests/                  # pytest
├── scripts/kill_app.sh     # tắt nhanh tiến trình aic-dev
└── .env.example

frontend/
├── package.json            # scripts: dev, build, start, lint
├── next.config.ts          # output standalone (dev) / export (Electron)
├── src/
│   ├── app/                # Next.js App Router
│   │   ├── (dashboard)/    # group route: dashboard, search, history, analysis, evaluation
│   │   └── layout.tsx
│   ├── components/         # ui + layout dùng chung
│   ├── config/env.ts       # đọc NEXT_PUBLIC_*
│   ├── lib/api/            # FetchApiClient + ApiError
│   └── features/           # vertical slice: video-search, dashboard, history, analysis, evaluation
└── .env.local
```

## Chạy dev

### 1. Backend

```bash
cd backend
uv sync --extra dev          # cài deps + ruff/pytest
cp .env.example .env         # tuỳ chỉnh KIS_DEMO_MODE, DATABASE_URL, KIS_LLM_*

# Chế độ demo — không cần dataset AIC, dùng fixture có sẵn
uv run aic-dev               # uvicorn 0.0.0.0:8000 với --reload

# Chế độ production-like — cần dữ liệu AIC thật đã đặt tại ./data
# (xem docs/SEARCH_PIPELINE.md để biết cấu trúc data/{clip-features-32,keyframes,objects,videos})
uv run aic-prepare-data      # sinh manifest.csv + collection.json
uv run aic-build-index       # build R-tree index ở ./data/search_index
uv run aic-dev
```

Backend mặc định lắng nghe tại <http://localhost:8000>.

| Đường dẫn | Mục đích |
|---|---|
| `/api/health` | Health check |
| `/docs` | Swagger UI |
| `/api/v1/kis/search/` | Single-shot hybrid retrieval |
| `/api/v1/kis/agent/search/` | Agentic retrieval (plan → search → eval → retry) |
| `/api/v1/kis/search/inspect/` | Inspect router & R-tree candidates |
| `/api/v1/kis/tools/*` | Planner/rerank/refine cho n8n |
| `/api/v1/dashboard/*` `/history/*` `/analysis/*` `/evaluation/*` `/runs/*` | Endpoints phụ trợ |

Tắt tiến trình dev đang bật: `./scripts/kill_app.sh`.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local .env.local.template   # nếu chưa có, tạo file mới với 2 dòng sau
```

Nội dung `.env.local`:

```env
NEXT_PUBLIC_USE_MOCKS=false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

```bash
npm run dev                # next dev
```

Frontend mặc định tại <http://localhost:3000>, gọi API ở `NEXT_PUBLIC_API_BASE_URL`.

### 3. PostgreSQL + Redis cho dev (tuỳ chọn)

Mặc định backend dùng SQLite (`./data/aic.db`). Khi cần Postgres/Redis (Celery, multi-worker):

```bash
docker compose -f docker/dev/docker-compose.yml up -d db n8n
# Postgres: localhost:5433 (user/pwd: aic/aic), n8n: localhost:5678
```

Sửa `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://aic:aic@localhost:5433/aic
```

## Kiểm tra & lint

```bash
# Backend
cd backend
uv run aic-lint            # ruff check src tests
uv run aic-test            # pytest

# Frontend
cd frontend
npm run lint               # eslint
```

## Biến môi trường đáng chú ý (backend/.env)

| Biến | Mặc định | Ghi chú |
|---|---|---|
| `KIS_DEMO_MODE` | `true` | `true` chạy offline với fixture; `false` cần build index thật |
| `KIS_DATA_ROOT` | `./data` | Thư mục chứa dataset AIC |
| `KIS_INDEX_ROOT` | `./data/search_index` | Output của `aic-build-index` |
| `KIS_EMBEDDING_URL` | `http://localhost:9000` | Remote embedding service (khi không dùng demo) |
| `KIS_LLM_API_KEY` / `KIS_LLM_ENDPOINT` / `KIS_LLM_MODEL` | rỗng | Để trống dùng deterministic planner offline; điền API OpenAI-compatible để bật LLM planner |
| `APP_CORS_ORIGINS` | `http://localhost:3000` | Thêm origin của frontend nếu chạy khác port |
| `APP_PUBLIC_BASE_URL` | `http://localhost:8000` | Base URL cho asset keyframe/video trả về |

## Tài liệu liên quan

- Pipeline dữ liệu + build index: [`docs/SEARCH_PIPELINE.md`](./docs/SEARCH_PIPELINE.md)
- Hướng dẫn demo cuối kỳ: [`docs/MIDTERM_DEMO_GUIDE.md`](./docs/MIDTERM_DEMO_GUIDE.md)
- Workflow n8n mẫu: `n8n/aic-agent-search.json`

## Quy ước

- Không commit `.env`, secret, dataset, build artifact, `node_modules`, `.venv`.
- BE/FE/electron giữ để tham khảu; mọi thay đổi mới ưu tiên vào `backend/` + `frontend/`.