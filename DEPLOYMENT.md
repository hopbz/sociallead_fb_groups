# Deployment guide

## 1. Chạy local trên Windows

```powershell
.\run_local_windows.ps1
```

Sau khi backend/frontend chạy xong, đăng nhập Facebook profile lần đầu:

```powershell
cd backend
.\.venv\Scripts\activate
python scripts\login_playwright.py
```

## 2. Chạy Docker Compose để deploy/VPS

```bash
cp .env.example .env
```

Sửa tối thiểu trong `.env`:

```env
API_TOKEN=token_manh_cua_em
POSTGRES_PASSWORD=mat_khau_postgres_manh
DATABASE_URL=postgresql+psycopg2://sociallead:mat_khau_postgres_manh@db:5432/sociallead_fb
HEADLESS=true
```

Chạy:

```bash
docker compose up --build -d
docker compose logs -f backend
```

Truy cập:

```txt
Frontend: http://localhost:3000
Backend docs: http://localhost:3001/docs
```

## 3. Profile Facebook trên server

Cách ổn nhất:

1. Chạy `python scripts/login_playwright.py` ở máy local có giao diện.
2. Đăng nhập Facebook thủ công.
3. Copy thư mục `backend/data/profiles` lên server vào đúng đường dẫn `backend/data/profiles`.
4. Trên server đặt `HEADLESS=true` rồi chạy Docker Compose.

Không dùng bypass CAPTCHA/checkpoint. Nếu Facebook yêu cầu xác minh, mở browser xử lý thủ công.

## 4. n8n

Import workflow:

```txt
n8n/scan_facebook_groups_http_request.json
```

HTTP Request node:

```txt
POST http://host.docker.internal:3001/api/v1/scan-groups
Header: X-API-Token: API_TOKEN trong .env
```

Body:

```json
{
  "engine": "playwright",
  "max_scrolls": 8,
  "max_posts_per_group": 50,
  "send_telegram": true,
  "write_google_sheets": true
}
```
