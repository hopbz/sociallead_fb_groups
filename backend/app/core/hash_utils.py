from __future__ import annotations

import hashlib
import re


def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or '').encode('utf-8')).hexdigest()


def content_hash(group_url: str, content: str) -> str:
    normalized = clean_text(content).lower()
    return sha256_text(f'{group_url}|{normalized[:2000]}')
