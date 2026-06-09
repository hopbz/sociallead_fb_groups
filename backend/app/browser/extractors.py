from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.hash_utils import clean_text, content_hash, sha256_text

POST_URL_PATTERNS = [
    r'/groups/[^/]+/posts/([^/?#]+)',
    r'/groups/[^/]+/permalink/([^/?#]+)',
    r'/posts/(\d+)',
    r'/permalink/(\d+)',
    r'/posts/([^/?#]+)',
    r'/permalink/([^/?#]+)',
    r'story_fbid=(\d+)',
    r'multi_permalinks=(\d+)',
    r'fbid=(\d+)',
]
POST_URL_KEYWORDS = ['/posts/', '/permalink/', 'story_fbid=', 'multi_permalinks=', 'fbid=']


@dataclass
class RawFacebookPost:
    group_url: str
    post_id: str
    content_hash: str
    post_url: str
    author: str
    content: str
    engine: str
    scraped_at: datetime


def extract_post_id(url: str, group_url: str, content: str) -> str:
    for pattern in POST_URL_PATTERNS:
        match = re.search(pattern, url or '')
        if match:
            return match.group(1)
    return sha256_text(f'{group_url}|{content[:800]}')[:32]


def pick_post_url(urls: list[str]) -> str:
    for url in urls:
        if any(key in url for key in POST_URL_KEYWORDS):
            return url
    return ''


def guess_author_from_text(text: str) -> str:
    lines = [line.strip() for line in (text or '').splitlines() if line.strip()]
    if not lines:
        return ''
    first = clean_text(lines[0])
    blocked = ('like', 'comment', 'share', 'thích', 'bình luận', 'chia sẻ', 'write a comment')
    if len(first) <= 80 and not first.lower().startswith(blocked):
        return first
    return ''


def make_post(group_url: str, content: str, post_url: str, engine: str) -> RawFacebookPost | None:
    content = clean_text(content)
    blocked_fragments = (
        'suggested for you',
        'people you may know',
        'reels',
        'write a comment',
    )
    if any(fragment in content.lower() for fragment in blocked_fragments) and len(content) < 120:
        return None
    if len(content) < 30:
        return None
    post_url = post_url or ''
    post_id = extract_post_id(post_url, group_url, content)
    return RawFacebookPost(
        group_url=group_url,
        post_id=post_id,
        content_hash=content_hash(group_url, content),
        post_url=post_url,
        author=guess_author_from_text(content),
        content=content,
        engine=engine,
        scraped_at=datetime.now(timezone.utc),
    )
