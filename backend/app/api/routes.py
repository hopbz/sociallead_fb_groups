from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.deps import verify_token
from app.config import Settings, get_settings
from app.core.group_metadata import (
    FacebookGroupMetadata,
    fallback_group_name,
    fetch_facebook_group_metadata,
    has_group_metadata,
    normalize_facebook_group_url,
    note_from_metadata,
)
from app.core.scanner import FacebookGroupScanner
from app.db.models import ErrorLog, GroupSource, Keyword, ScanRun, ScrapedPost
from app.db.session import get_db
from app.schemas import (
    DashboardOut,
    EngineName,
    ErrorLogOut,
    GroupSourceCreate,
    GroupSourceOut,
    GroupSourceUpdate,
    KeywordCreate,
    KeywordOut,
    LoginStatusOut,
    PostOut,
    ScanRequest,
    ScanResponse,
    ScanRunOut,
    SettingsOut,
)

router = APIRouter(prefix='/api/v1')


@router.get('/health')
def health(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return {
        'ok': True,
        'app': settings.app_name,
        'default_engine': settings.default_engine,
        'headless': settings.headless,
        'scheduler_enabled': settings.scheduler_enabled,
    }


@router.get('/dashboard', response_model=DashboardOut, dependencies=[Depends(verify_token)])
def dashboard(db: Session = Depends(get_db)) -> DashboardOut:
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    groups_total = db.scalar(select(func.count(GroupSource.id))) or 0
    groups_active = db.scalar(select(func.count(GroupSource.id)).where(GroupSource.is_active == True)) or 0
    keywords_total = db.scalar(select(func.count(Keyword.id)).where(Keyword.is_active == True)) or 0
    posts_total = db.scalar(select(func.count(ScrapedPost.id))) or 0
    posts_today = db.scalar(select(func.count(ScrapedPost.id)).where(ScrapedPost.created_at >= today_start)) or 0
    runs_total = db.scalar(select(func.count(ScanRun.id))) or 0
    errors_total = db.scalar(select(func.count(ErrorLog.id))) or 0
    last_run = db.execute(select(ScanRun).order_by(desc(ScanRun.started_at)).limit(1)).scalar_one_or_none()
    recent_posts = db.execute(select(ScrapedPost).order_by(desc(ScrapedPost.created_at)).limit(10)).scalars().all()
    recent_runs = db.execute(select(ScanRun).order_by(desc(ScanRun.started_at)).limit(8)).scalars().all()

    daily_posts = []
    for i in range(6, -1, -1):
        day = today_start - timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = db.scalar(select(func.count(ScrapedPost.id)).where(ScrapedPost.created_at >= day, ScrapedPost.created_at < next_day)) or 0
        daily_posts.append({'label': day.strftime('%d/%m'), 'value': int(count)})

    return DashboardOut(
        groups_total=groups_total,
        groups_active=groups_active,
        keywords_total=keywords_total,
        posts_total=posts_total,
        posts_today=posts_today,
        runs_total=runs_total,
        errors_total=errors_total,
        last_run=last_run,
        recent_posts=recent_posts,
        recent_runs=recent_runs,
        daily_posts=daily_posts,
    )


@router.get('/groups', response_model=list[GroupSourceOut], dependencies=[Depends(verify_token)])
def list_groups(db: Session = Depends(get_db)):
    return db.execute(select(GroupSource).order_by(desc(GroupSource.created_at))).scalars().all()


@router.post('/groups', response_model=GroupSourceOut, dependencies=[Depends(verify_token)])
def create_group(payload: GroupSourceCreate, settings: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    group_url = normalize_facebook_group_url(payload.url)
    metadata = fetch_facebook_group_metadata([group_url], settings).get(group_url)
    group_name = metadata.name if metadata else (payload.name.strip() or fallback_group_name(group_url))
    if not metadata:
        metadata = FacebookGroupMetadata(name=group_name, privacy='unknown')
    note = note_from_metadata(metadata, payload.note)
    group = GroupSource(name=group_name, url=group_url, is_active=payload.is_active, note=note)
    db.add(group)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f'Không thể tạo group: {exc}') from exc
    db.refresh(group)
    return group


@router.post('/groups/refresh-metadata', response_model=list[GroupSourceOut], dependencies=[Depends(verify_token)])
def refresh_group_metadata(settings: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    groups = db.execute(select(GroupSource).order_by(desc(GroupSource.created_at))).scalars().all()
    groups_to_refresh = [group for group in groups if not has_group_metadata(group.note)]
    urls = [normalize_facebook_group_url(group.url) for group in groups_to_refresh]
    metadata_by_url = fetch_facebook_group_metadata(urls, settings)

    for group, normalized_url in zip(groups_to_refresh, urls):
        metadata = metadata_by_url.get(normalized_url)
        if not metadata:
            metadata = FacebookGroupMetadata(name=group.name or fallback_group_name(normalized_url), privacy='unknown')
        group.url = normalized_url
        group.name = metadata.name or group.name
        group.note = note_from_metadata(metadata, group.note)
        db.add(group)

    if groups_to_refresh:
        db.commit()
    return db.execute(select(GroupSource).order_by(desc(GroupSource.created_at))).scalars().all()


@router.patch('/groups/{group_id}', response_model=GroupSourceOut, dependencies=[Depends(verify_token)])
def update_group(group_id: str, payload: GroupSourceUpdate, db: Session = Depends(get_db)):
    group = db.get(GroupSource, group_id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.delete('/groups/{group_id}', dependencies=[Depends(verify_token)])
def delete_group(group_id: str, db: Session = Depends(get_db)):
    group = db.get(GroupSource, group_id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    db.delete(group)
    db.commit()
    return {'ok': True}


@router.get('/keywords', response_model=list[KeywordOut], dependencies=[Depends(verify_token)])
def list_keywords(db: Session = Depends(get_db)):
    return db.execute(select(Keyword).order_by(desc(Keyword.created_at))).scalars().all()


@router.post('/keywords', response_model=KeywordOut, dependencies=[Depends(verify_token)])
def create_keyword(payload: KeywordCreate, db: Session = Depends(get_db)):
    keyword = Keyword(keyword=payload.keyword.strip(), is_active=payload.is_active)
    db.add(keyword)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f'Không thể tạo keyword: {exc}') from exc
    db.refresh(keyword)
    return keyword


@router.patch('/keywords/{keyword_id}', response_model=KeywordOut, dependencies=[Depends(verify_token)])
def toggle_keyword(keyword_id: str, is_active: bool = Query(...), db: Session = Depends(get_db)):
    kw = db.get(Keyword, keyword_id)
    if not kw:
        raise HTTPException(status_code=404, detail='Keyword not found')
    kw.is_active = is_active
    db.add(kw)
    db.commit()
    db.refresh(kw)
    return kw


@router.delete('/keywords/{keyword_id}', dependencies=[Depends(verify_token)])
def delete_keyword(keyword_id: str, db: Session = Depends(get_db)):
    kw = db.get(Keyword, keyword_id)
    if not kw:
        raise HTTPException(status_code=404, detail='Keyword not found')
    db.delete(kw)
    db.commit()
    return {'ok': True}


@router.get('/posts', response_model=list[PostOut], dependencies=[Depends(verify_token)])
def list_posts(limit: int = Query(50, ge=1, le=300), q: str | None = None, db: Session = Depends(get_db)):
    stmt = select(ScrapedPost).order_by(desc(ScrapedPost.created_at)).limit(limit)
    if q:
        stmt = select(ScrapedPost).where(ScrapedPost.content.ilike(f'%{q}%')).order_by(desc(ScrapedPost.created_at)).limit(limit)
    return db.execute(stmt).scalars().all()


@router.get('/runs', response_model=list[ScanRunOut], dependencies=[Depends(verify_token)])
def list_runs(limit: int = Query(30, ge=1, le=100), db: Session = Depends(get_db)):
    return db.execute(select(ScanRun).order_by(desc(ScanRun.started_at)).limit(limit)).scalars().all()


@router.get('/errors', response_model=list[ErrorLogOut], dependencies=[Depends(verify_token)])
def list_errors(limit: int = Query(30, ge=1, le=100), db: Session = Depends(get_db)):
    return db.execute(select(ErrorLog).order_by(desc(ErrorLog.created_at)).limit(limit)).scalars().all()


@router.get('/settings', response_model=SettingsOut, dependencies=[Depends(verify_token)])
def get_runtime_settings(settings: Settings = Depends(get_settings)):
    return SettingsOut(
        default_engine=settings.default_engine,
        headless=settings.headless,
        login_wait_timeout_seconds=settings.login_wait_timeout_seconds,
        facebook_latest_sorting=settings.facebook_latest_sorting,
        max_scrolls_per_group=settings.max_scrolls_per_group,
        max_posts_per_group=settings.max_posts_per_group,
        retry_times=settings.retry_times,
        scheduler_enabled=settings.scheduler_enabled,
        scheduler_interval_minutes=settings.scheduler_interval_minutes,
        telegram_enabled=settings.telegram_enabled,
        google_sheets_enabled=settings.google_sheets_enabled,
    )


@router.post('/login/{engine}', dependencies=[Depends(verify_token)])
def login_profile(engine: EngineName, settings: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    scanner = FacebookGroupScanner(settings, db)
    scanner.ensure_login(engine)
    status = scanner.login_status(engine)
    return {'ok': True, 'engine': engine, 'message': 'Login profile saved', **status}


@router.get('/login-status/{engine}', response_model=LoginStatusOut, dependencies=[Depends(verify_token)])
def login_status(engine: EngineName, settings: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    scanner = FacebookGroupScanner(settings, db)
    return LoginStatusOut(engine=engine, **scanner.login_status(engine))


@router.post('/scan-groups', response_model=ScanResponse, dependencies=[Depends(verify_token)])
def scan_groups(payload: ScanRequest, settings: Settings = Depends(get_settings), db: Session = Depends(get_db)):
    scanner = FacebookGroupScanner(settings, db)
    return scanner.scan(payload)


@router.post('/scan-groups/background', dependencies=[Depends(verify_token)])
def scan_groups_background(payload: ScanRequest, background_tasks: BackgroundTasks, settings: Settings = Depends(get_settings)):
    def run_bg():
        from app.db.session import SessionLocal
        with SessionLocal() as db:
            FacebookGroupScanner(settings, db).scan(payload)
    background_tasks.add_task(run_bg)
    return {'ok': True, 'message': 'Scan started in background'}
