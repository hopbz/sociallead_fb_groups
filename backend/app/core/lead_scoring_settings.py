from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.config import Settings
from app.core.env_file import update_env_file
from app.db.models import AppSetting

LEAD_SCORING_KEY = 'lead_scoring_settings'


def default_lead_scoring_settings(settings: Settings) -> dict[str, Any]:
    return {
        'score_threshold': settings.lead_score_threshold,
        'niche_name': settings.lead_niche_name,
        'positive_keywords': _split_keywords(settings.lead_positive_keywords),
        'negative_keywords': _split_keywords(settings.lead_negative_keywords),
        'comment_tone': settings.lead_comment_tone,
        'max_posts_per_group': settings.lead_max_posts_per_group,
        'scan_interval_minutes': settings.lead_scan_interval_minutes,
    }


def get_lead_scoring_settings(settings: Settings, db: Session) -> dict[str, Any]:
    defaults = default_lead_scoring_settings(settings)
    row = db.get(AppSetting, LEAD_SCORING_KEY)
    if not row:
        return defaults

    try:
        stored = json.loads(row.value)
    except (TypeError, json.JSONDecodeError):
        return defaults
    if not isinstance(stored, dict):
        return defaults
    return {**defaults, **stored}


def save_lead_scoring_settings(db: Session, values: dict[str, Any]) -> None:
    serialized = json.dumps(values, ensure_ascii=False)
    row = db.get(AppSetting, LEAD_SCORING_KEY)
    if row:
        row.value = serialized
    else:
        db.add(AppSetting(key=LEAD_SCORING_KEY, value=serialized))
    db.commit()


def save_lead_scoring_env(values: dict[str, Any]) -> None:
    update_env_file({
        'LEAD_SCORE_THRESHOLD': values['score_threshold'],
        'LEAD_NICHE_NAME': values['niche_name'],
        'LEAD_POSITIVE_KEYWORDS': ', '.join(values['positive_keywords']),
        'LEAD_NEGATIVE_KEYWORDS': ', '.join(values['negative_keywords']),
        'LEAD_COMMENT_TONE': values['comment_tone'],
        'LEAD_MAX_POSTS_PER_GROUP': values['max_posts_per_group'],
        'LEAD_SCAN_INTERVAL_MINUTES': values['scan_interval_minutes'],
    })


def _split_keywords(value: str) -> list[str]:
    return [item.strip() for item in value.split(',') if item.strip()]
