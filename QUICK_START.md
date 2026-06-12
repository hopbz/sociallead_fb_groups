# 🚀 Quick Start Guide - SocialLead Facebook Groups Scraper

## 📋 Yêu cầu
- **Windows 10/11** hoặc **macOS/Linux**
- **Python 3.10+**
- **Node.js 18+** (cho frontend)
- **Google Chrome/Edge** cài đặt sẵn (hoặc Playwright sẽ tự tải)

## 🎯 Cài đặt (Setup) - 3 bước

### 1️⃣ Clone hoặc tải dự án
```bash
cd c:\Python  # Windows
cd ~/projects  # macOS/Linux
# Bạn đã có dự án tại: c:\Python\sociallead_fb_groups
cd sociallead_fb_groups
```

### 2️⃣ Setup Backend (Python)
```powershell
# Windows PowerShell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
```

```bash
# macOS/Linux
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

### 3️⃣ Setup Frontend (Node.js)
```bash
cd frontend
npm install --legacy-peer-deps
```

## 🔐 Đăng nhập Facebook

**⚠️ Lưu ý quan trọng:**
- Chỉ dùng browser automation với Playwright/SeleniumBase
- Đăng nhập bằng tài khoản Facebook thực của bạn
- Không bypass CAPTCHA - xử lý thủ công khi Facebook yêu cầu
- Dữ liệu lưu trong thư mục `data/profiles/`

### Đăng nhập sử dụng CDP Playwright (Khuyến nghị)
```bash
cd backend
.\.venv\Scripts\Activate.ps1  # Windows
# hoặc: source .venv/bin/activate  # macOS/Linux
python scripts/login_cdp_playwright.py
```

Sau đó:
1. Cửa sổ trình duyệt sẽ mở ra
2. Đăng nhập Facebook thủ công
3. Nếu có **Checkpoint** → xử lý theo hướng dẫn trên màn hình
4. Khi xong, nhấn **Enter** trong terminal
5. Profile sẽ được lưu tại: `backend/data/profiles/cdp_playwright_fb/`

### Các lựa chọn khác:

**Playwright (backup):**
```bash
python scripts/login_playwright.py
```

**SeleniumBase (UC Mode):**
```bash
python scripts/login_seleniumbase.py
```

## ▶️ Chạy Ứng dụng

### Option 1: Chạy tự động (All-in-one)
```powershell
# Windows - mở PowerShell từ thư mục dự án
.\run_local_windows.ps1
```

Sau ~30 giây, truy cập:
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:3001/docs

### Option 2: Chạy thủ công từng phần

**Terminal 1 - Backend:**
```bash
cd backend
.\.venv\Scripts\Activate.ps1  # Windows
# hoặc: source .venv/bin/activate  # macOS/Linux
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Truy cập:
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:3001
- **API Docs:** http://localhost:3001/docs

## 📱 Sử dụng Ứng dụng

### Bước 1: Thêm Facebook Groups
1. Truy cập http://localhost:3000
2. Đăng nhập (API_TOKEN mặc định: `YsLS7X_wdy1ahvcpxs5WMf7TCui4qnoxl31KwWWLvwo`)
3. Vào **Settings** → **Groups**
4. Nhấn **+ Add Group**
5. Dán URL Facebook Group, ví dụ:
   - `https://www.facebook.com/groups/123456789`
   - `https://www.facebook.com/groups/groupname`

### Bước 2: Thêm Keyword (tùy chọn)
1. Vào **Settings** → **Keywords**
2. Nhấn **+ Add Keyword**
3. Nhập từ khóa cần lọc, ví dụ: "việc làm", "tuyển dụng", "freelance"
4. Ấn Save

### Bước 3: Quét Groups
1. Vào **Scanner**
2. Chọn **Engine**: 
   - `cdp_playwright` (mặc định, tốt nhất)
   - `playwright` (nhanh hơn)
   - `seleniumbase` (fallback)
3. Thiết lập:
   - **Max Scrolls:** 8 (tăng để lấy nhiều bài hơn)
   - **Posts per Group:** 50
   - **Send Telegram:** Tắt (trừ khi đã cấu hình)
   - **Write Google Sheets:** Tắt (trừ khi đã cấu hình)
4. Nhấn **Scan**

### Bước 4: Xem Kết quả
- **Posts:** Tất cả bài viết đã scrape
- **Runs:** Lịch sử quét
- **Errors:** Ghi chép lỗi
- **CSV Export:** Tải file CSV từ `backend/data/output/`

## 📊 Dashboard Chính
Hiển thị:
- Tổng số Groups, Keywords, Posts, Runs
- Biểu đồ bài viết 7 ngày qua
- Bài viết mới nhất
- Quét gần nhất

## 🔧 Tùy chỉnh (.env)
File `.env` trong thư mục dự án:

```env
# App
API_TOKEN=YsLS7X_wdy1ahvcpxs5WMf7TCui4qnoxl31KwWWLvwo
DEFAULT_ENGINE=cdp_playwright
HEADLESS=false

# Browser behavior
MAX_SCROLLS_PER_GROUP=8
MAX_POSTS_PER_GROUP=50
BROWSER_SLOW_MO_MS=80  # Delay để tránh bị phát hiện (ms)
PAGE_LOAD_TIMEOUT_MS=45000
SCROLL_WAIT_SECONDS=2.5

# Scheduler (tự động quét)
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_MINUTES=30

# Optional: Telegram notifications
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Optional: Google Sheets
GOOGLE_SHEETS_ENABLED=false
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_JSON=data/service_account.json
```

## 🗄️ Dữ liệu được Lưu

```
backend/data/
├── profiles/
│   ├── cdp_playwright_fb/     # Chrome profile (CDP)
│   ├── playwright_fb/          # Playwright profile
│   └── seleniumbase_fb/        # SeleniumBase profile
├── output/
│   └── facebook_group_posts.csv  # CSV export
├── screenshots/                # Ảnh chụp khi lỗi
└── logs/
    └── app.log                 # Logs ứng dụng

Database: backend/data/sociallead_local.db (SQLite)
```

## 🐛 Xử lý Lỗi Thường Gặp

### "Profile chưa đăng nhập"
```bash
# Chạy lại đăng nhập
python scripts/login_cdp_playwright.py
```

### "Checkpoint/CAPTCHA"
1. Một cửa sổ trình duyệt sẽ mở ra
2. Đăng nhập Facebook
3. Xử lý checkpoint/CAPTCHA thủ công
4. Nhấn Enter trong terminal khi xong

### "Không tìm thấy bài viết"
- Tăng `MAX_SCROLLS_PER_GROUP` trong `.env` (ví dụ: 15)
- Kiểm tra Group có cho phép xem bài viết không
- Thử engine khác: `DEFAULT_ENGINE=playwright`

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Frontend không kết nối Backend
- Kiểm tra Backend chạy tại `http://localhost:3001`
- Kiểm tra file `.env` trong `frontend/`: `VITE_API_BASE_URL=http://localhost:3001`
- Restart frontend: `npm run dev`

## 🌐 Deploy (Docker)

### Local Docker
```bash
docker compose up --build -d
```

Truy cập:
- Frontend: http://localhost:3000
- Backend: http://localhost:3001

### VPS/Production
Xem chi tiết: [DEPLOYMENT.md](DEPLOYMENT.md)

## 📌 API Endpoints Chính

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/v1/health` | Kiểm tra backend |
| POST | `/api/v1/scan-groups` | Quét groups |
| GET | `/api/v1/dashboard` | Dashboard |
| POST | `/api/v1/groups` | Thêm group |
| GET | `/api/v1/groups` | Danh sách groups |
| POST | `/api/v1/keywords` | Thêm keyword |
| GET | `/api/v1/keywords` | Danh sách keywords |
| GET | `/api/v1/posts` | Danh sách posts đã scrape |

Xem toàn bộ: http://localhost:3001/docs

## 📞 Support & Troubleshooting

Kiểm tra logs:
```bash
tail -f backend/data/logs/app.log  # macOS/Linux
Get-Content backend/data/logs/app.log -Wait  # Windows PowerShell
```

## 🎓 Tìm Hiểu Thêm

- **Architecture:** [README.md](README.md)
- **Deployment:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **n8n Integration:** Xem `n8n/` folder
- **API Docs:** http://localhost:3001/docs (khi chạy backend)

## ✅ Checklist Lần Đầu Chạy

- [ ] ✅ Python 3.10+ cài đặt
- [ ] ✅ Node.js 18+ cài đặt
- [ ] ✅ Backend venv & dependencies
- [ ] ✅ Frontend node_modules
- [ ] ✅ Playwright browsers
- [ ] ✅ Facebook đăng nhập
- [ ] ✅ Backend startup (port 3001)
- [ ] ✅ Frontend startup (port 3000)
- [ ] ✅ Thêm Facebook Groups
- [ ] ✅ Chạy Scan lần đầu

---

**Mục tiêu:** Scrape bài viết từ Facebook Groups một cách an toàn, không bypass CAPTCHA/checkpoint, chỉ dùng browser automation hợp lệ. 🎯
