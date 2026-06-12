# SocialLead OS — Facebook Groups SaaS

Bản fullstack đã được tinh gọn từ dự án SocialLead OS, chỉ tập trung vào **Facebook Group Scraper / Monitoring**.

> Phạm vi an toàn: hệ thống chỉ dùng browser automation với Playwright/SeleniumBase theo hướng đăng nhập thủ công và dùng profile local. Không có chức năng bypass CAPTCHA/checkpoint, né anti-bot, spam, auto-login trái phép, hay truy cập group/tài khoản mà em không có quyền xem.

## 1. Tính năng

- Backend FastAPI.
- Frontend React + Vite, chỉnh lại theo style SocialLead OS nhưng bỏ toàn bộ module không cần thiết.
- Database PostgreSQL khi deploy Docker; SQLite khi chạy local nhanh.
- Playwright scraper chính + SeleniumBase scraper fallback.
- UI quản lý Facebook Groups.
- UI quản lý keyword filter.
- Anti-duplicate theo `post_id` và `content_hash`.
- Lưu bài viết vào database + CSV.
- Google Sheets output tùy chọn.
- Telegram alert tùy chọn.
- API `/api/v1/scan-groups` cho n8n gọi.
- Batch scheduler tự quét theo phút.
- Log lỗi từng group.
- Screenshot khi lỗi.
- Retry nhẹ khi page chưa load.
- Dashboard, scraped posts, run history, error logs, settings.

## 2. Cấu trúc

```txt
sociallead_fb_groups_fullstack/
├── backend/                 # FastAPI + Playwright + SeleniumBase
├── frontend/                # React/Vite dashboard
├── database/                # PostgreSQL init schema
├── n8n/                     # Workflow mẫu gọi API scan
├── docker-compose.yml
├── .env.example             # Env cho Docker Compose
├── run_local_windows.ps1
├── DEPLOYMENT.md
└── README.md
```

## 3. Chạy local trên Windows

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env
python scripts\login_playwright.py
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

Backend docs:

```txt
http://localhost:3001/docs
```

### Frontend

Mở terminal thứ hai:

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend:

```txt
http://localhost:3000
```

Khi vào UI, nhập:

```txt
Backend URL: http://localhost:3001
API Token: change-this-token
```

Với backend local mặc định, token `change-this-token` không bị enforce mạnh để em dễ test. Khi deploy thật, hãy đổi `API_TOKEN`.

## 4. Chạy nhanh bằng script Windows

```powershell
.\run_local_windows.ps1
```

Sau đó vẫn nên chạy login profile:

```powershell
cd backend
.\.venv\Scripts\activate
python scripts\login_playwright.py
```

## 5. Deploy bằng Docker Compose

```bash
cp .env.example .env
```

Sửa `.env` tối thiểu:

```env
API_TOKEN=token_manh_cua_em
POSTGRES_PASSWORD=mat_khau_postgres_manh
DATABASE_URL=postgresql+psycopg2://sociallead:mat_khau_postgres_manh@db:5432/sociallead_fb
HEADLESS=true
```

Chạy:

```bash
docker compose up --build -d
```

Truy cập:

```txt
Frontend: http://localhost:3000
Backend:  http://localhost:3001/docs
Postgres: localhost:5432
```

## 6. Đăng nhập Facebook profile

Playwright:

```powershell
cd backend
.\.venv\Scripts\activate
python scripts\login_playwright.py
```

SeleniumBase:

```powershell
python scripts\login_seleniumbase.py
```

Trên VPS không có GUI, cách ổn nhất là đăng nhập local trước, sau đó copy thư mục này lên server:

```txt
backend/data/profiles
```

## 7. Dùng UI

1. Vào `http://localhost:3000`.
2. Nhập Backend URL và API Token.
3. Vào **Facebook Groups** thêm group URL.
4. Vào **Keyword Filter** thêm keyword.
5. Vào **Run Scanner** chọn engine và chạy.
6. Xem kết quả ở **Scraped Posts**, **Run History**, **Error Logs**.

Nếu không có keyword active, backend sẽ lưu tất cả bài mới nhìn thấy. Nếu có keyword active, chỉ lưu/gửi alert các bài có chứa keyword.

## 8. API cho n8n

Endpoint:

```txt
POST http://localhost:3001/api/v1/scan-groups
Header: X-API-Token: <API_TOKEN trong .env>
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

Workflow mẫu:

```txt
n8n/scan_facebook_groups_http_request.json
```

## 9. Telegram

Trong `.env` backend hoặc `.env` Docker:

```env
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=token_bot_cua_em
TELEGRAM_CHAT_ID=8850401551
```

## 10. Google Sheets

Đặt file service account tại:

```txt
backend/data/service_account.json
```

Sửa `.env`:

```env
GOOGLE_SHEETS_ENABLED=true
GOOGLE_SHEETS_SPREADSHEET_ID=id_google_sheet_cua_em
GOOGLE_SHEETS_WORKSHEET_NAME=Facebook Group Posts
GOOGLE_SERVICE_ACCOUNT_JSON=data/service_account.json
```

Nhớ share Google Sheet cho email service account quyền Editor.

## 11. Dữ liệu sinh ra

```txt
backend/data/output/facebook_group_posts.csv
backend/data/logs/app.log
backend/data/screenshots/
backend/data/profiles/
```

## 12. Lưu ý vận hành

- Chỉ thêm group mà tài khoản Facebook của em có quyền xem.
- Không chạy tốc độ quá nhanh.
- Nếu Facebook yêu cầu xác minh, xử lý thủ công trên trình duyệt.
- Với deploy server, đặt `HEADLESS=true` và dùng profile đã login từ local.
