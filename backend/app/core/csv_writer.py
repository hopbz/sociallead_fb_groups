from __future__ import annotations

import csv
from pathlib import Path

from app.db.models import ScrapedPost


def append_posts_to_csv(path: Path, posts: list[ScrapedPost]) -> None:
    if not posts:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    fields = [
        'created_at', 'scraped_at', 'group_url', 'group_name', 'post_id',
        'post_url', 'author', 'matched_keywords', 'engine', 'content'
    ]
    with path.open('a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            writer.writeheader()
        for p in posts:
            writer.writerow({
                'created_at': str(p.created_at or ''),
                'scraped_at': str(p.scraped_at or ''),
                'group_url': p.group_url,
                'group_name': p.group_name or '',
                'post_id': p.post_id or '',
                'post_url': p.post_url or '',
                'author': p.author or '',
                'matched_keywords': p.matched_keywords or '',
                'engine': p.engine,
                'content': p.content,
            })
