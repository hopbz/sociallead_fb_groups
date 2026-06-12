# 🔧 Troubleshooting Guide - SocialLead Facebook Groups Scraper

## Common Issues & Solutions

### 🔴 Backend Issues

#### ❌ "ModuleNotFoundError: No module named 'app'"
**Cause:** Python path not configured correctly
**Solution:**
```bash
cd backend
python -c "from app.main import app; print('OK')"
```
If error persists:
```bash
# Delete and reinstall venv
Remove-Item .venv -Recurse -Force
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### ❌ "Port 3001 already in use"
**Cause:** Backend already running on that port
**Solution:**
```bash
# Find and kill process on port 3001 (Windows)
netstat -ano | findstr :3001
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --port 3002
```

#### ❌ "Cannot connect to database"
**Cause:** SQLite database not initialized
**Solution:**
```bash
cd backend
python -c "from app.db.session import init_db; init_db(); print('DB OK')"
```

#### ❌ "ImportError: cannot import name 'stealth_sync' from 'playwright_stealth'"
**Status:** ✅ FIXED - Updated imports to use `stealth()` instead of `stealth_sync()`

---

### 🟠 Frontend Issues

#### ❌ "Cannot find module 'react'"
**Cause:** node_modules not installed
**Solution:**
```bash
cd frontend
npm install --legacy-peer-deps
```

#### ❌ "EACCES: permission denied" (macOS/Linux)
**Cause:** Permission issues
**Solution:**
```bash
sudo chown -R $USER:$USER frontend/node_modules
npm install
```

#### ❌ "Frontend blank page / Cannot reach backend"
**Cause:** Backend not running or wrong URL
**Solution:**
1. Check backend is running: http://localhost:3001/docs
2. Check frontend `.env`: `VITE_API_BASE_URL=http://localhost:3001`
3. Restart frontend: `npm run dev`

#### ❌ "ERR! code ERESOLVE"
**Cause:** Dependency conflicts
**Solution:**
```bash
npm install --legacy-peer-deps
```

---

### 🟡 Playwright & Browser Issues

#### ❌ "No browser found"
**Cause:** Playwright browsers not installed
**Solution:**
```bash
python -m playwright install chromium --with-deps
```

#### ❌ "Chrome executable not found"
**Cause:** Chrome/Edge not installed or Playwright cache corrupted
**Solution:**
```bash
# Option 1: Install Chrome
# https://www.google.com/chrome

# Option 2: Reinstall Playwright
python -m playwright uninstall chromium
python -m playwright install chromium --with-deps
```

#### ❌ "CDP connection refused"
**Cause:** Chrome CDP port already in use
**Solution:**
```bash
# Kill any running Chrome processes
taskkill /F /IM chrome.exe

# Or wait a few seconds for port to free up
```

---

### 🟠 Facebook Login Issues

#### ❌ "Profile chưa đăng nhập"
**Cause:** Facebook session expired or profile not saved
**Solution:**
```bash
# Re-login with your engine
python scripts/login_cdp_playwright.py
# or
python scripts/login_playwright.py
# or
python scripts/login_seleniumbase.py
```

#### ❌ "Checkpoint/CAPTCHA xuất hiện"
**What to do:**
1. A browser window will open automatically
2. Follow Facebook's checkpoint/CAPTCHA process manually
3. When done, press **Enter** in the terminal
4. Profile will be saved

**If still stuck:**
```bash
# Try different engine
python scripts/login_playwright.py
```

#### ❌ "Không tìm thấy bài viết" (No posts found)
**Cause:** Group is private, no posts, or not scrolling enough
**Solution 1:** Increase scrolls
```bash
# In .env:
MAX_SCROLLS_PER_GROUP=15  # Increase from 8
```

**Solution 2:** Try different engine
```bash
# In .env:
DEFAULT_ENGINE=playwright  # or seleniumbase
```

**Solution 3:** Check group URL
```bash
# Make sure group URL format is correct:
https://www.facebook.com/groups/123456789
# NOT: https://www.facebook.com/groups/groupname/
```

#### ❌ "Tài khoản không có quyền xem group này"
**Cause:** Not a member of the group or group is completely private
**Solution:**
1. Join the group manually on Facebook
2. Make sure your account can see the group
3. Try logging in again: `python scripts/login_cdp_playwright.py`

---

### 🟢 Data/Output Issues

#### ❌ "CSV file not created"
**Cause:** No posts scraped or CSV writing disabled
**Solution:**
```bash
# Check if posts were scraped
# Go to Dashboard → Posts

# Check CSV output setting - should be enabled by default
# File location: backend/data/output/facebook_group_posts.csv
```

#### ❌ "Screenshots not saved on error"
**Cause:** Permission issue or directory not created
**Solution:**
```bash
# Ensure directory exists
mkdir -p backend/data/screenshots
chmod 755 backend/data/screenshots  # macOS/Linux only
```

#### ❌ "Cannot connect to Google Sheets"
**Cause:** Service account not configured
**Solution:**
1. Create Google Cloud project and service account
2. Download JSON key to: `backend/data/service_account.json`
3. Share spreadsheet with service account email
4. Set in `.env`:
```env
GOOGLE_SHEETS_ENABLED=true
GOOGLE_SHEETS_SPREADSHEET_ID=your_id
```

---

### 🔵 Scheduler Issues

#### ❌ "Scheduler not running"
**Cause:** Scheduler disabled in .env
**Solution:**
```bash
# In .env:
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_MINUTES=30
```

#### ❌ "Scheduler scan skipped"
**Cause:** Profile not logged in when scheduler runs
**Solution:**
1. Make sure to login first: `python scripts/login_cdp_playwright.py`
2. Keep backend running
3. Check logs: `backend/data/logs/app.log`

---

### 🟣 n8n Integration Issues

#### ❌ "Cannot call API from n8n"
**Cause:** Wrong endpoint or authentication
**Solution in n8n:**
```json
{
  "method": "POST",
  "url": "http://your-backend:3001/api/v1/scan-groups",
  "headers": {
    "X-API-Token": "YOUR_API_TOKEN",
    "Content-Type": "application/json"
  },
  "body": {
    "engine": "cdp_playwright",
    "max_scrolls": 8,
    "max_posts_per_group": 50
  }
}
```

Check API token in `.env`:
```bash
API_TOKEN=YsLS7X_wdy1ahvcpxs5WMf7TCui4qnoxl31KwWWLvwo
```

---

### 📋 Verification Steps

#### Check Backend Status
```bash
# Test API
curl http://localhost:3001/api/v1/health

# Should return:
# {"ok":true,"app":"SocialLead Facebook Groups Backend",...}
```

#### Check Frontend Status
```bash
# Open in browser
http://localhost:3000

# Should see login page or dashboard
```

#### Check Database
```bash
# Backend needs to be running first
cd backend
python -c "
from app.db.session import SessionLocal
from app.db.models import GroupSource
with SessionLocal() as db:
    count = db.query(GroupSource).count()
    print(f'Groups in DB: {count}')
"
```

#### Check Logs
```bash
# Show last 50 lines of log
Get-Content backend/data/logs/app.log -Tail 50

# Or follow log in real-time
Get-Content backend/data/logs/app.log -Wait
```

---

### 🆘 Getting Help

1. **Check logs first:**
   ```bash
   backend/data/logs/app.log
   ```

2. **Run verification script:**
   ```bash
   python verify_setup.py
   ```

3. **Check if browser is working:**
   ```bash
   python -m playwright install --verbose chromium
   ```

4. **Test individual components:**
   ```bash
   # Test imports
   python -c "from app.main import app; print('OK')"
   
   # Test database
   python -c "from app.db.session import init_db; init_db(); print('OK')"
   
   # Test scraper
   python -c "from app.browser.cdp_playwright_scraper import CdpPlaywrightFacebookGroupScraper; print('OK')"
   ```

---

### 💡 Tips for Success

1. **Always login first** before trying to scan groups
2. **Use CDP Playwright** (DEFAULT_ENGINE=cdp_playwright) - it's the most reliable
3. **Keep browser slow** to avoid detection: BROWSER_SLOW_MO_MS=80+
4. **Don't run multiple scans simultaneously** - one at a time
5. **Handle checkpoints manually** - don't try to bypass
6. **Check logs** before troubleshooting - they usually tell you what's wrong
7. **Use Firefox/Safari on Linux** if Chrome has issues

---

### 🚨 Critical Requirements

- ✅ **Python 3.10+** installed
- ✅ **Node.js 18+** installed  
- ✅ **Chrome/Edge browser** installed (or let Playwright download it)
- ✅ **Facebook account** that can access target groups
- ✅ **First time**: Run login script to create profile
- ✅ **Port 3000, 3001** available (not in use)

---

### 📞 Performance Tips

If scraping is slow:

1. **Reduce scrolls:**
   ```env
   MAX_SCROLLS_PER_GROUP=5  # Instead of 8
   ```

2. **Reduce posts:**
   ```env
   MAX_POSTS_PER_GROUP=30  # Instead of 50
   ```

3. **Speed up browser:**
   ```env
   BROWSER_SLOW_MO_MS=50  # Instead of 80 (be careful!)
   SCROLL_WAIT_SECONDS=2.0  # Instead of 2.5
   ```

4. **Use Playwright instead of CDP:**
   ```env
   DEFAULT_ENGINE=playwright
   ```

---

## Still Have Issues?

1. Read full documentation: [QUICK_START.md](QUICK_START.md)
2. Check API documentation: http://localhost:3001/docs
3. Review logs: `backend/data/logs/app.log`
4. Run verification: `python verify_setup.py`

**Remember:** Most issues are solved by re-logging in or restarting the app.
