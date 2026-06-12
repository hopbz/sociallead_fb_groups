# 🚀 GET STARTED IN 3 COMMANDS

## For First-Time Setup (Do This Once)

### Command 1: Verify Installation
```powershell
python verify_setup.py
```
This checks that everything is installed. Should show all ✅ PASS.

### Command 2: Login to Facebook
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts/login_cdp_playwright.py
```
- Browser opens → Login with Facebook → Handle checkpoint if appears → Press Enter when done
- Your profile is saved for future runs

### Command 3: Start the Application
```powershell
.\run.ps1
```
- Starts backend (http://localhost:3001)
- Starts frontend (http://localhost:3000)
- Both in separate windows

---

## After That

### Open Browser
Go to: **http://localhost:3000**

### Add a Facebook Group
Settings → Groups → + Add Group → Paste URL → Save

Examples:
```
https://www.facebook.com/groups/123456789
https://www.facebook.com/groups/your_group_name
```

### (Optional) Add Keywords
Settings → Keywords → + Add Keyword → Type word to filter → Save

Examples: "việc làm", "tuyển dụng", "bán", "cần"

### Start Scraping
Scanner → Select engine → Adjust settings → Click Scan

### View Results
Dashboard → See stats + charts
Posts → See all scraped posts
CSV file → `backend/data/output/facebook_group_posts.csv`

---

## Each Time After (Restart App)

Just run:
```powershell
.\run.ps1
```

Done! ✅

---

## Troubleshooting

If something doesn't work:

1. **Check logs:** `Get-Content backend/data/logs/app.log -Tail 20`
2. **Read guide:** Open `QUICK_START.md` or `TROUBLESHOOTING.md`
3. **Verify setup:** `python verify_setup.py`
4. **Re-login:** `python scripts/login_cdp_playwright.py`

---

**That's it! You're ready to scrape Facebook groups.** 🎉
