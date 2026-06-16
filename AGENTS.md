# AGENTS.md — SocialLead OS Upgrade Guide

## Project Goal

Upgrade this project into an AI-assisted Facebook Group lead qualification workspace.

## Main Requirements

1. Fix scanned posts page:
   - The scraper must collect top-level Facebook group posts only.
   - Do not store comments or replies as posts.
   - Frontend "Bài viết đã quét" should display only posts, not comments.
   - Add backend filtering and frontend fallback filtering.

2. Add AI lead workflow support:
   - Add `processed_at` to scanned posts.
   - Add lead candidate persistence.
   - Add API to fetch unprocessed posts.
   - Add API to save AI-qualified leads.
   - Add API to mark a post as processed.
   - Add API to list lead candidates for dashboard usage.

3. Add n8n workflow documentation/export:
   - Schedule trigger.
   - Scan groups.
   - Fetch unprocessed posts.
   - AI score 1–10.
   - Save leads with score >= 7.
   - Send Telegram message.
   - Mark all analyzed posts as processed.

4. Improve frontend:
   - Add/upgrade Lead Candidates page.
   - Show score, group, author, post link, reason, suggested comment, status.
   - Add filters by score/status/group.
   - Add copy suggested comment button.
   - Add open post button.

## Validation Commands

Backend:

```bash
cd backend
python -m pytest
python -m compileall app
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run build
npm run lint
```

## Expected Output From Codex

For every task:

- Explain changed files.
- Show how to run/test.
- Mention any migration needed.
- Do not remove existing features.
- Do not introduce unsafe automation.
