# docker-compose tự đọc `.env` ở **cùng thư mục** với file compose, không đọc root.

## Dev

```bash
cd docker/dev
cp .env.example .env       # optional — defaults đã có sẵn trong compose
docker compose up -d
```

## Production

```bash
cd docker/production
cp .env.example .env       # rồi sửa các biến muốn override
# lưu ý NEXT_PUBLIC_API_BASE_URL và NEXT_PUBLIC_USE_MOCKS là build-time,
# đổi xong phải chạy lại:
docker compose up -d --build
```

Compose tự fallback về giá trị mặc định trong file `:-aic` khi biến không có trong `.env`, nên bỏ qua file `.env` cũng được — chỉ cần khi muốn override.
