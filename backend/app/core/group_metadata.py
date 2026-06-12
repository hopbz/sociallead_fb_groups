from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from app.config import Settings

logger = logging.getLogger(__name__)

PRIVATE_SIGNALS = (
    'private group',
    'nhom rieng tu',
    'nhóm riêng tư',
    'rieng tu',
    'riêng tư',
)
PUBLIC_SIGNALS = (
    'public group',
    'nhom cong khai',
    'nhóm công khai',
    'cong khai',
    'công khai',
)


@dataclass
class FacebookGroupMetadata:
    name: str
    privacy: str | None = None


def normalize_facebook_group_url(raw_url: str) -> str:
    value = raw_url.strip()
    if not re.match(r'^https?://', value, re.IGNORECASE):
        value = f'https://{value}'

    parsed = urlparse(value)
    path_parts = [part for part in parsed.path.split('/') if part]
    try:
        groups_index = [part.lower() for part in path_parts].index('groups')
        group_id = path_parts[groups_index + 1]
    except (ValueError, IndexError):
        return value

    return f'https://www.facebook.com/groups/{group_id}'


def fallback_group_name(group_url: str) -> str:
    parsed = urlparse(group_url)
    path_parts = [part for part in parsed.path.split('/') if part]
    try:
        groups_index = [part.lower() for part in path_parts].index('groups')
        group_slug = path_parts[groups_index + 1]
    except (ValueError, IndexError):
        return parsed.netloc.replace('www.', '') or group_url
    return re.sub(r'[-_.]+', ' ', group_slug).strip() or group_slug


def note_from_metadata(metadata: FacebookGroupMetadata, user_note: str | None = None) -> str:
    payload = {
        'facebook_group_metadata': {
            'name': metadata.name,
            'privacy': metadata.privacy or 'unknown',
        }
    }
    if user_note:
        payload['user_note'] = user_note
    return json.dumps(payload, ensure_ascii=False)


def metadata_from_note(note: str | None) -> FacebookGroupMetadata | None:
    if not note:
        return None
    try:
        payload = json.loads(note)
    except (TypeError, json.JSONDecodeError):
        return None
    metadata = payload.get('facebook_group_metadata') if isinstance(payload, dict) else None
    if not isinstance(metadata, dict):
        return None
    name = str(metadata.get('name') or '').strip()
    privacy = str(metadata.get('privacy') or '').strip().lower() or None
    if not name and not privacy:
        return None
    return FacebookGroupMetadata(name=name, privacy=privacy)


def has_group_metadata(note: str | None) -> bool:
    metadata = metadata_from_note(note)
    return bool(metadata and metadata.name and metadata.privacy in {'public', 'private', 'unknown'})


def _clean_title(raw_title: str) -> str:
    title = re.sub(r'\s+', ' ', raw_title or '').strip()
    title = re.sub(r'\s*\|\s*Facebook.*$', '', title, flags=re.IGNORECASE).strip()
    blocked_titles = {'facebook', 'groups', 'log into facebook', 'log in to facebook', 'đăng nhập facebook'}
    if title.lower() in blocked_titles:
        return ''
    return title


def _detect_privacy(page_text: str) -> str | None:
    lowered = (page_text or '').lower()
    if any(signal in lowered for signal in PRIVATE_SIGNALS):
        return 'private'
    if any(signal in lowered for signal in PUBLIC_SIGNALS):
        return 'public'
    return None


def fetch_facebook_group_metadata(group_urls: list[str], settings: Settings) -> dict[str, FacebookGroupMetadata]:
    if not group_urls:
        return {}

    results: dict[str, FacebookGroupMetadata] = {}
    timeout_ms = min(settings.page_load_timeout_ms, 15_000)

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(settings.playwright_profile_dir),
                headless=settings.headless,
                slow_mo=settings.browser_slow_mo_ms,
                viewport={'width': 1365, 'height': 850},
                locale='vi-VN',
                args=['--disable-dev-shm-usage', '--no-sandbox'],
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.set_default_timeout(timeout_ms)
            for group_url in group_urls:
                try:
                    page.goto(group_url, wait_until='domcontentloaded', timeout=timeout_ms)
                    page.wait_for_timeout(2500)
                    raw = page.evaluate(
                        """() => {
                            const metaTitle = document.querySelector('meta[property="og:title"]')?.content || '';
                            const h1 = Array.from(document.querySelectorAll('h1'))
                                .map(el => el.innerText.trim())
                                .find(Boolean) || '';
                            return {
                                title: h1 || metaTitle || document.title || '',
                                text: document.body?.innerText || ''
                            };
                        }"""
                    )
                    name = _clean_title(str(raw.get('title') or ''))
                    privacy = _detect_privacy(str(raw.get('text') or ''))
                    if name or privacy:
                        results[group_url] = FacebookGroupMetadata(
                            name=name or fallback_group_name(group_url),
                            privacy=privacy,
                        )
                except Exception as exc:
                    logger.info('Could not fetch Facebook group metadata url=%s error=%s', group_url, exc)
                    continue
            context.close()
    except Exception as exc:
        logger.warning('Facebook group metadata is unavailable; using URL fallback: %s', exc)

    return results
