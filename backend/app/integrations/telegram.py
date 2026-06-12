from __future__ import annotations

import html
import logging

import requests
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import AppSetting, ScrapedPost

logger = logging.getLogger(__name__)


TELEGRAM_ENABLED_KEY = 'telegram_enabled'
TELEGRAM_CHAT_ID_KEY = 'telegram_chat_id'


def get_telegram_settings(settings: Settings, db: Session) -> dict[str, object]:
    enabled_row = db.get(AppSetting, TELEGRAM_ENABLED_KEY)
    chat_id_row = db.get(AppSetting, TELEGRAM_CHAT_ID_KEY)
    enabled = settings.telegram_enabled
    if enabled_row:
        enabled = enabled_row.value.strip().lower() in {'1', 'true', 'yes', 'on'}
    chat_id = chat_id_row.value.strip() if chat_id_row else settings.telegram_chat_id.strip()
    return {
        'enabled': enabled,
        'chat_id': chat_id,
        'bot_token_configured': bool(settings.telegram_bot_token.strip()),
    }


def save_telegram_settings(db: Session, *, enabled: bool, chat_id: str) -> None:
    values = {
        TELEGRAM_ENABLED_KEY: 'true' if enabled else 'false',
        TELEGRAM_CHAT_ID_KEY: chat_id.strip(),
    }
    for key, value in values.items():
        row = db.get(AppSetting, key)
        if row:
            row.value = value
        else:
            db.add(AppSetting(key=key, value=value))
    db.commit()


def send_telegram_message(settings: Settings, chat_id: str, text: str) -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError('Telegram bot token chưa được cấu hình trong biến môi trường.')
    if not chat_id:
        raise RuntimeError('Telegram chat ID chưa được cấu hình.')

    url = f'https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage'
    response = requests.post(url, json={
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }, timeout=15)
    response.raise_for_status()


def send_telegram_posts(settings: Settings, posts: list[ScrapedPost], db: Session) -> None:
    if not posts:
        return
    telegram = get_telegram_settings(settings, db)
    if not telegram['enabled']:
        return
    chat_id = str(telegram['chat_id'])
    if not telegram['bot_token_configured'] or not chat_id:
        logger.warning('Telegram is enabled but token/chat_id is missing')
        return

    for post in posts[:30]:
        text = (
            '🚀 <b>SocialLead OS - Facebook Group Match</b>\n\n'
            f'<b>Group:</b> {html.escape(post.group_name or post.group_url)}\n'
            f'<b>Keyword:</b> {html.escape(post.matched_keywords or "") }\n'
            f'<b>Author:</b> {html.escape(post.author or "Unknown")}\n\n'
            f'{html.escape(post.content[:900])}\n\n'
            f'{html.escape(post.post_url or post.group_url)}'
        )
        try:
            send_telegram_message(settings, chat_id, text)
        except Exception as exc:
            logger.exception('Telegram send failed: %s', exc)
