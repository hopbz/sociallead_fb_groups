from __future__ import annotations


def normalize_keywords(keywords: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in keywords:
        kw = (item or '').strip()
        if not kw:
            continue
        key = kw.lower()
        if key not in seen:
            seen.add(key)
            result.append(kw)
    return result


def match_keywords(content: str, keywords: list[str]) -> list[str]:
    if not keywords:
        return []
    text = (content or '').lower()
    return [kw for kw in keywords if kw.lower() in text]
