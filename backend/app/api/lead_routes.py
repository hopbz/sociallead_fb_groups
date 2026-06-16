from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import verify_token
from app.config import Settings, get_settings
from app.core.lead_scoring_settings import (
    get_lead_scoring_settings,
    save_lead_scoring_env,
    save_lead_scoring_settings,
)
from app.db.models import LeadCandidate, ScrapedPost
from app.db.session import get_db

router = APIRouter(
    prefix='/api/v1',
    tags=['lead-automation'],
    dependencies=[Depends(verify_token)],
)


class PostForAI(BaseModel):
    id: str
    group_name: str | None = None
    group_url: str | None = None
    post_url: str | None = None
    author: str | None = None
    content: str
    created_at: datetime | None = None

    model_config = {'from_attributes': True}


class LeadCreate(BaseModel):
    post_id: str
    group_name: str | None = None
    group_url: str | None = None
    post_url: str | None = None
    author: str | None = None
    content: str = Field(min_length=1)
    score: int = Field(ge=1, le=10)
    need_stage: str | None = None
    persona: str | None = None
    pain_points: str | None = None
    reason: str | None = None
    suggested_comment: str = Field(min_length=1)


LeadStatus = Literal['new', 'reviewed', 'contacted', 'won', 'lost']


class LeadOut(BaseModel):
    id: str
    post_id: str
    group_name: str | None = None
    group_url: str | None = None
    post_url: str | None = None
    author: str | None = None
    content: str
    score: int
    need_stage: str | None = None
    persona: str | None = None
    pain_points: str | None = None
    reason: str | None = None
    suggested_comment: str
    status: LeadStatus
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class LeadScoringSettings(BaseModel):
    score_threshold: int = Field(default=7, ge=1, le=10)
    niche_name: str = Field(default='Dịch vụ địa phương', min_length=1, max_length=120)
    positive_keywords: list[str] = Field(default_factory=list, max_length=100)
    negative_keywords: list[str] = Field(default_factory=list, max_length=100)
    comment_tone: str = Field(default='Tự nhiên, hữu ích và lịch sự.', min_length=1, max_length=500)
    max_posts_per_group: int = Field(default=30, ge=1, le=100)
    scan_interval_minutes: int = Field(default=30, ge=15, le=1440)


@router.get('/posts/unprocessed', response_model=list[PostForAI])
def get_unprocessed_posts(
    limit: int = Query(default=50, ge=1, le=300),
    db: Session = Depends(get_db),
):
    return db.execute(
        select(ScrapedPost)
        .where(ScrapedPost.processed_at.is_(None))
        .order_by(desc(ScrapedPost.created_at))
        .limit(limit)
    ).scalars().all()


@router.patch('/posts/{post_id}/processed')
def mark_post_processed(post_id: str, db: Session = Depends(get_db)):
    post = db.get(ScrapedPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')

    post.processed_at = datetime.now(timezone.utc)
    db.add(post)
    db.commit()
    return {'ok': True, 'post_id': post_id}


@router.post('/leads')
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    source_post = db.get(ScrapedPost, payload.post_id)
    if not source_post:
        raise HTTPException(status_code=404, detail='Source post not found')

    existing = db.execute(
        select(LeadCandidate).where(LeadCandidate.post_id == payload.post_id)
    ).scalar_one_or_none()
    if existing:
        return {'ok': True, 'lead_id': existing.id, 'duplicated': True}

    lead = LeadCandidate(**payload.model_dump(), status='new')
    db.add(lead)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(LeadCandidate).where(LeadCandidate.post_id == payload.post_id)
        ).scalar_one()
        return {'ok': True, 'lead_id': existing.id, 'duplicated': True}

    db.refresh(lead)
    return {'ok': True, 'lead_id': lead.id, 'duplicated': False}


@router.get('/leads', response_model=list[LeadOut])
def list_leads(
    limit: int = Query(default=100, ge=1, le=500),
    min_score: int | None = Query(default=None, ge=1, le=10),
    status: LeadStatus | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(LeadCandidate)
    if min_score is not None:
        stmt = stmt.where(LeadCandidate.score >= min_score)
    if status is not None:
        stmt = stmt.where(LeadCandidate.status == status)
    query = (q or '').strip()
    if query:
        pattern = f'%{query}%'
        stmt = stmt.where(or_(
            LeadCandidate.group_name.ilike(pattern),
            LeadCandidate.author.ilike(pattern),
            LeadCandidate.content.ilike(pattern),
            LeadCandidate.reason.ilike(pattern),
        ))
    return db.execute(
        stmt.order_by(desc(LeadCandidate.score), desc(LeadCandidate.created_at)).limit(limit)
    ).scalars().all()


@router.patch('/leads/{lead_id}/status', response_model=LeadOut)
def update_lead_status(
    lead_id: str,
    payload: LeadStatusUpdate,
    db: Session = Depends(get_db),
):
    lead = db.get(LeadCandidate, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail='Lead not found')
    lead.status = payload.status
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get('/settings/lead-scoring', response_model=LeadScoringSettings)
def read_lead_scoring_settings(
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    return get_lead_scoring_settings(settings, db)


@router.put('/settings/lead-scoring', response_model=LeadScoringSettings)
def update_lead_scoring_settings(
    payload: LeadScoringSettings,
    db: Session = Depends(get_db),
):
    values = payload.model_dump()
    values['positive_keywords'] = _normalize_keywords(values['positive_keywords'])
    values['negative_keywords'] = _normalize_keywords(values['negative_keywords'])
    save_lead_scoring_settings(db, values)
    save_lead_scoring_env(values)
    get_settings.cache_clear()
    return values


def _normalize_keywords(keywords: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in keywords:
        keyword = value.strip()
        key = keyword.casefold()
        if not keyword or key in seen:
            continue
        seen.add(key)
        normalized.append(keyword)
    return normalized
