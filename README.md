# AIC Video Retrieval Platform

Hệ thống tìm kiếm video/keyframe cho AI Challenge, sử dụng hybrid retrieval theo `domain routing + object bag-of-words + PCA/R-tree + exact CLIP rerank`.

Phiên bản này có thêm lớp **Agentic AI**: phân tích mục tiêu tiếng Việt, lập kế hoạch truy xuất, gọi search tool, tự đánh giá Top-K và viết lại truy vấn để tìm lại tối đa một lần. Agent chạy offline bằng planner xác định để demo ổn định; khi khai báo API tương thích OpenAI (ví dụ MiniMax), hệ thống tự dùng LLM planner và tự quay về offline planner nếu API lỗi.

## Demo hoàn chỉnh không cần tải dataset lớn

Yêu cầu: Docker Compose, Python 3 và `ffmpeg` (nếu thiếu ffmpeg vẫn tạo keyframe, chỉ bỏ qua video minh họa).

```bash
cp .env.example .env
sh scripts/run_demo.sh
```

Sau khi hệ thống healthy:

- Giao diện Agent: <http://localhost:3000/kis/search>
- Agent API: `POST http://localhost:8000/api/kis/agent/search/`
- Swagger: <http://localhost:8000/api/docs/>
- n8n: <http://localhost:5678>

Import workflow n8n đã bàn giao:

```bash
docker compose -f docker-compose.yml -f docker-compose.demo.yml \
  exec n8n n8n import:workflow --input=/workflows/aic-agent-search.json
```

Truy vấn demo khuyến nghị: `Tìm cảnh một người đang đi xe đạp ngoài đường`.

```bash
curl -X POST http://localhost:8000/api/kis/agent/search/ \
  -H 'Content-Type: application/json' \
  -d '{"query":"Tìm cảnh một người đang đi xe đạp ngoài đường","top_k":6,"max_attempts":2}'
```

Để chuyển sang dữ liệu AIC thật, dùng `docker-compose.yml` không kèm file demo, tải/giải nén dữ liệu theo `docs/SEARCH_PIPELINE.md`, rồi build index. API và frontend không phải sửa.

Hướng dẫn đầy đủ về dữ liệu đầu vào, kiến trúc, download/validate/build index và cách chạy cho học sinh nằm tại [docs/SEARCH_PIPELINE.md](./docs/SEARCH_PIPELINE.md).

## Công nghệ

- Backend: Python 3.12, Django 5, Django REST Framework, PostgreSQL, Redis, Celery, Gunicorn.
- Frontend: Node 24, React 19, TypeScript, Vite, Tailwind CSS, React Router, Zod.
- Runtime: Docker Compose và Nginx.

## Chạy nhanh bằng Docker

Yêu cầu Docker Engine/Desktop có Docker Compose v2.

```bash
cp .env.example .env
docker compose build backend
docker compose run --rm backend python -m data_processing.cli prepare --data-root /data/aic
docker compose run --rm backend python manage.py build_kis_index
docker compose up
```

Sau khi các container healthy:

- Frontend: <http://localhost:3000>
- Backend health check: <http://localhost:8000/api/health/>
- Swagger UI: <http://localhost:8000/api/docs/>
- Search routing inspect: `POST http://localhost:8000/api/kis/search/inspect/`
- Django Admin: <http://localhost:8000/admin/>

Tạo tài khoản quản trị:

```bash
docker compose exec backend python manage.py createsuperuser
```

Dừng hệ thống:

```bash
docker compose down
```

Dữ liệu PostgreSQL, Redis, static và media nằm trong named volumes. Chỉ dùng `docker compose down -v` khi chủ động muốn xóa toàn bộ dữ liệu local.

## Chạy từng phần để phát triển

Có thể chỉ bật hạ tầng bằng Docker:

```bash
docker compose up -d db redis
```

Sau đó làm theo [README backend](./BE/README.md) và [README frontend](./FE/README.md). Cấu hình mặc định publish PostgreSQL tại `localhost:5433` và Redis tại `localhost:6380` để tránh đụng các dịch vụ local; có thể đổi bằng `POSTGRES_PORT` và `REDIS_PORT` trong `.env`. Khi BE chạy ngoài Docker với hạ tầng Compose, cập nhật `DB_PORT=5433`, `CELERY_BROKER_URL=redis://127.0.0.1:6380/0` và `CELERY_RESULT_BACKEND=redis://127.0.0.1:6380/1` trong `BE/.env`.

## Cấu trúc

```text
.
├── BE/                  # Django API và background worker
│   ├── data_processing/ # Download, validate, manifest
│   └── search_engine/   # Domain router, BoW, R-tree, reranker
├── FE/                  # React SPA
├── docs/                # Kiến trúc và hướng dẫn pipeline
├── docker-compose.yml   # Toàn bộ stack local/container
├── .env.example         # Biến môi trường cấp Compose
└── README.md
```

Quy ước: không commit `.env`, secret, database dump, file upload, `node_modules`, build artifact hay virtual environment.
