from __future__ import annotations

import html
import logging

import requests

from app.config import Settings
from app.db.models import ScrapedPost

logger = logging.getLogger(__name__)


def send_telegram_posts(settings: Settings, posts: list[ScrapedPost]) -> None:
    if not posts or not settings.telegram_enabled:
        return
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning('Telegram is enabled but token/chat_id is missing')
        return

    url = f'https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage'
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
            requests.post(url, json={
                'chat_id': settings.telegram_chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True,
            }, timeout=15)
        except Exception as exc:
            logger.exception('Telegram send failed: %s', exc)
