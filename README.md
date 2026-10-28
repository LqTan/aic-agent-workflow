# AIC Video Retrieval & Agentic Search System

Hệ thống truy vấn và tìm kiếm video thông minh (Agentic Video Retrieval) phục vụ cuộc thi AI Challenge (AIC). Dự án kết hợp mô hình thị giác CLIP (ONNX), chỉ mục lai (Hybrid Indexing: vector + object Bag-of-Words + domain routing) và giao diện trực quan.

---

## 🏗️ Cấu trúc dự án

Dự án được tinh gọn thành 2 thành phần chính:

```text
AIC-main/
├── backend/            # FastAPI Service (Clean Architecture / DDD)
│   ├── models/         # Model ONNX CLIP và Tokenizer (In-process inference)
│   ├── src/app/        # Mã nguồn backend (video_search, search_engine, dashboard...)
│   └── pyproject.toml  # Cấu hình dependencies của Backend
├── frontend/           # Next.js 16 (App Router) + React 19 + Tailwind CSS v4
│   ├── src/            # Giao diện dashboard, search, evaluation, history
│   └── package.json    # Cấu hình dependencies frontend
├── data/               # Dữ liệu video, keyframes, clip features và search index
├── docker/             # Cấu hình Docker Compose (dev và production)
└── n8n/                # Workflow Agentic Search kết hợp LLM
```

---

## 🚀 Hướng dẫn khởi chạy nhanh (Quick Start)

### Yêu cầu môi trường
- **Python**: `>= 3.12` (khuyên dùng trình quản lý package **`uv`**)
- **Node.js**: `>= 20` và `npm`
- **Docker**: Dùng để chạy PostgreSQL và n8n

---

### Bước 1: Khởi động Cơ sở dữ liệu (PostgreSQL)

Chạy container PostgreSQL 17 từ thư mục `docker/dev`:

```bash
docker compose -f docker/dev/docker-compose.yml up -d db
```
*(Cổng mặc định: `5433`, thông tin đăng nhập: `aic:aic`)*

---

### Bước 2: Khởi động Backend (FastAPI - Cổng 8000)

Mở terminal tại thư mục `backend`:

```bash
cd backend
```

**Cách 1: Sử dụng `uv` (Nhanh nhất):**
```bash
# 1. Cài đặt toàn bộ thư viện cần thiết
uv sync

# 2. (Tùy chọn) Nạp metadata 7.800 keyframe từ manifest.csv vào PostgreSQL
uv run aic-import-manifest

# 3. Chạy server phát triển (hỗ trợ hot-reload)
uv run aic-dev
```

**Cách 2: Sử dụng Python 3 & pip tiêu chuẩn (cho Windows / máy không dùng `uv`):**
```bash
# 1. Tạo và kích hoạt môi trường ảo
python -m venv .venv
# Trên Windows: .venv\Scripts\activate
# Trên Linux:   source .venv/bin/activate

# 2. Cài đặt dependencies từ pyproject.toml
pip install -e .

# 3. Chạy server
python -m uvicorn app.main:app --reload --port 8000
```

- API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### Bước 3: Khởi động Frontend (Next.js - Cổng 3000)

Mở terminal thứ hai tại thư mục `frontend`:

```bash
cd frontend

# 1. Cài đặt thư viện giao diện
npm install

# 2. Khởi động giao diện Next.js
npm run dev
```

- Truy cập web: [http://localhost:3000](http://localhost:3000)

---

## 🛠️ Các lệnh CLI hữu ích trong Backend

Trong thư mục `backend/`, bạn có thể chạy nhanh các tác vụ bằng `uv run`:

| Lệnh | Ý nghĩa |
| :--- | :--- |
| `uv run aic-dev` | Khởi động server FastAPI ở cổng 8000 với hot-reload |
| `uv run aic-import-manifest` | Nạp metadata từ `data/manifest.csv` vào bảng `keyframes` trong DB |
| `uv run aic-prepare-data` | Quét dataset, tạo `manifest.csv` và tự động đồng bộ vào DB |
| `uv run aic-build-index` | Xây dựng lại search index lai từ dữ liệu trong `data/` |
| `uv run aic-test` | Chạy bộ kiểm thử tự động (pytest) |
| `uv run aic-lint` | Kiểm tra định dạng code với Ruff |

---

## ⚙️ Biến môi trường quan trọng (`.env`)

Sao chép từ file mẫu nếu cần tùy biến:
```bash
cp .env.example .env
```

- **`DATABASE_URL`**: Kết nối PostgreSQL (`postgresql+psycopg://aic:aic@localhost:5433/aic`).
- **`KIS_EMBEDDING_PROVIDER`**: Mặc định là `onnx` (nhúng trực tiếp model CLIP nội bộ trong backend, không cần server inference riêng).
- **`KIS_DATA_ROOT`**: Đường dẫn tới thư mục chứa dataset (`./data`).
- **`KIS_INDEX_ROOT`**: Đường dẫn tới index tìm kiếm (`./data/search_index`).
- **`KIS_LLM_API_KEY` / `KIS_LLM_ENDPOINT`**: Cấu hình LLM Planner (OpenAI-compatible) cho tính năng Agent Search (để trống nếu dùng offline local planner).
