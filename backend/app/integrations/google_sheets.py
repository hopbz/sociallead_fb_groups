from __future__ import annotations

import logging

import gspread

from app.config import Settings
from app.db.models import ScrapedPost

logger = logging.getLogger(__name__)

HEADER = [
    'created_at', 'scraped_at', 'group_name', 'group_url', 'post_id', 'post_url',
    'author', 'matched_keywords', 'engine', 'content'
]


def write_posts_to_google_sheets(settings: Settings, posts: list[ScrapedPost]) -> None:
    if not posts or not settings.google_sheets_enabled:
        return
    if not settings.google_sheets_spreadsheet_id:
        logger.warning('Google Sheets is enabled but spreadsheet id is missing')
        return
    if not settings.google_service_account_json.exists():
        logger.warning('Google service account file not found: %s', settings.google_service_account_json)
        return
    try:
        client = gspread.service_account(filename=str(settings.google_service_account_json))
        spreadsheet = client.open_by_key(settings.google_sheets_spreadsheet_id)
        try:
            sheet = spreadsheet.worksheet(settings.google_sheets_worksheet_name)
        except gspread.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(title=settings.google_sheets_worksheet_name, rows=1000, cols=len(HEADER))
            sheet.append_row(HEADER)
        values = []
        for p in posts:
            values.append([
                str(p.created_at or ''),
                str(p.scraped_at or ''),
                p.group_name or '',
                p.group_url,
                p.post_id or '',
                p.post_url or '',
                p.author or '',
                p.matched_keywords or '',
                p.engine,
                p.content,
            ])
        sheet.append_rows(values, value_input_option='USER_ENTERED')
    except Exception as exc:
        logger.exception('Google Sheets write failed: %s', exc)
