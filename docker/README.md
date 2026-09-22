# Docker Compose — môi trường

Thư mục này chứa 2 file `docker-compose.yml` tách biệt theo môi trường, **root repo không có compose nào**.

## `docker/dev/docker-compose.yml`

Chỉ chạy các phụ thuộc bên ngoài. Frontend + backend chạy trực tiếp trên máy dev bằng `npm` và `uv` để tận dụng HMR / watch.

**Bật / tắt:**
```bash
docker compose -f docker/dev/docker-compose.yml up -d
docker compose -f docker/dev/docker-compose.yml down
```

**Services:**
- `db` (Postgres 17) — port `${POSTGRES_PORT:-5433}` → 5432 trong container
- `n8n` — port `${N8N_PORT:-5678}`

**Sau khi `up -d`, chạy local:**
```bash
# Terminal 1 — backend
cd backend
uv sync --extra dev
DATABASE_URL=postgresql+psycopg://aic:aic@localhost:5433/aic \
  uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Mở:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1/kis/search/
- n8n: http://localhost:5678
- Postgres: `localhost:5433` (user/pass: `aic`/`aic`, db: `aic`)

## `docker/production/docker-compose.yml`

Full stack: `db` + `backend` (uvicorn) + `frontend` (Next.js prod build) + `n8n`.

**Bật / tắt:**
```bash
docker compose -f docker/production/docker-compose.yml up -d --build
docker compose -f docker/production/docker-compose.yml down
```

**Services & ports:**
- `db` → `${POSTGRES_PORT:-5433}:5432`
- `backend` → `${BACKEND_PORT:-8000}:8000`
- `frontend` → `${FRONTEND_PORT:-3000}:3000` (build-time truyền `NEXT_PUBLIC_API_BASE_URL` qua ARG)
- `n8n` → `${N8N_PORT:-5678}:5678`

**Biến môi trường** (override trước khi `up`):
```bash
KIS_LLM_API_KEY=sk-xxx \
KIS_LLM_ENDPOINT=https://api.openai.com/v1/chat/completions \
KIS_LLM_MODEL=gpt-4o-mini \
NEXT_PUBLIC_USE_MOCKS=false \
  docker compose -f docker/production/docker-compose.yml up -d --build
```

## Biến môi trường chung

Xem `.env.example` ở mỗi service:
- `backend/.env.example` — backend
- `frontend/.env.local` — frontend (chỉ override khi dev ngoài docker)

## Volumes (persistent)

- `postgres_data` — Postgres data
- `backend_index` — search index (vector DB) ở `/data/search_index`
- `backend_data` — uploaded videos + keyframes ở `/data/aic`
- `n8n_data` — workflow history
