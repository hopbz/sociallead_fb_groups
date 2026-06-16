# SocialLead OS

SocialLead OS is an AI-assisted Facebook Group lead qualification workspace.
It collects top-level group posts that the signed-in account can view, filters
comments and replies, and sends new posts through a human-reviewed AI workflow.

o automatic Facebook comments.

- No spam, account farms, or proxy farms.
- Only scan groups the account is allowed to view.
- AI comments are drafts; a human must review and publish them manually.
- Use conservative limits and a 30–60 minute scan interval.

## Architecture

- Backend: FastAPI, SQLAlchemy 2, SQLite locally or PostgreSQL with Docker.
- Frontend: React 19, TypeScript, Vite and Tailwind CSS.
- Browser engines: CDP Playwright, Playwright and SeleniumBase.
- Automation: importable n8n workflow with AI qualification and Telegram.

## Backend setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

Copy `.env.example` to `.env` and replace all placeholder secrets first.
API documentation is available at `http://localhost:3001/docs`.

## Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` and authenticate with the `API_TOKEN` configured
for the backend.

## Browser session

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts/login_cdp_playwright.py
```

Log in manually. Any Facebook CAPTCHA or checkpoint must also be completed
manually. The session profile is stored under `backend/data/profiles/`.

## Demo mode

Demo mode creates fake scanned posts and lead candidates without scanning
Facebook or using real personal data:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m scripts.seed_demo
```

The seed is idempotent. Open **Bài viết đã quét** and **Lead tiềm năng** after
starting the backend and frontend.

## Lead workflow

The **Lead tiềm năng** page supports:

- score, need stage, group, author and content preview;
- qualification reason and suggested comment;
- filters by score, status and group/content keyword;
- copy comment and open original post;
- statuses: `new`, `reviewed`, `contacted`, `won`, `lost`.

The **Cấu hình** page supports niche, score threshold, positive and negative
keywords, comment tone, posts per group and scan interval.

## n8n and Telegram

1. Read [docs/n8n-ai-lead-workflow.md](docs/n8n-ai-lead-workflow.md).
2. Import `n8n/workflows/ai_lead_workflow.json`.
3. Configure `BACKEND_BASE_URL`, `BACKEND_API_TOKEN`, `TELEGRAM_CHAT_ID` and
   `AI_API_KEY` on the n8n host.
4. Select OpenAI and Telegram credentials in n8n.
5. Run the manual trigger and inspect every node before activating the schedule.

Telegram settings for the built-in scanner are available on the frontend
configuration page. The bot token stays in environment variables.

## Database and migrations

Local mode defaults to `backend/data/sociallead_local.db`. Docker Compose uses
PostgreSQL. Backend startup creates missing tables and applies small additive
schema updates.

For PostgreSQL, the explicit lead migration is:

```powershell
psql "$env:DATABASE_URL" -f database/migrations/20260612_add_lead_automation.sql
```

Always backup a database before manual migration or cleanup.

## Main API endpoints

| Method    | Endpoint                            | Purpose                      |
| --------- | ----------------------------------- | ---------------------------- |
| `POST`    | `/api/v1/scan-groups`               | Scan configured groups       |
| `GET`     | `/api/v1/posts`                     | List scanned posts           |
| `GET`     | `/api/v1/posts/unprocessed`         | List posts awaiting AI       |
| `PATCH`   | `/api/v1/posts/{post_id}/processed` | Mark a post processed        |
| `POST`    | `/api/v1/leads`                     | Save a lead idempotently     |
| `GET`     | `/api/v1/leads`                     | List lead candidates         |
| `PATCH`   | `/api/v1/leads/{lead_id}/status`    | Update lead status           |
| `GET/PUT` | `/api/v1/settings/lead-scoring`     | Read/update scoring settings |

Protected endpoints require the `X-API-Token` header.

## Troubleshooting

### Frontend cannot connect

- Confirm backend health at `http://localhost:3001/api/v1/health`.
- Check the frontend API base URL and `X-API-Token`.
- Confirm CORS includes `http://localhost:3000`.
- In Vite development, using `http://localhost:3000` as the API base routes
  `/api` through the built-in proxy to backend port `3001`.

### Playwright or Chrome fails

- Close Chrome processes using the same profile.
- Check write access to `backend/data/profiles`.
- Run `python -m playwright install chromium`.
- Complete CAPTCHA/checkpoint manually; the project does not bypass them.

### Database migration fails

- Restore from backup before retrying.
- Check DDL permissions and backend logs.
- Do not delete the production database as a migration workaround.

### n8n cannot reach backend

- From Docker, try `http://host.docker.internal:3001`.
- On the same Docker network, try `http://backend:3001`.
- Verify `BACKEND_API_TOKEN` matches backend `API_TOKEN`.
- Test `/api/v1/health` from inside the n8n runtime.

## Validation

```powershell
cd backend
python -m compileall app
python -m pytest

cd ..\frontend
npm run build
```

See [QUICK_START.md](QUICK_START.md) and [DEPLOYMENT.md](DEPLOYMENT.md) for
additional setup and deployment details.
