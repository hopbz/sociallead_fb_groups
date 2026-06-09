from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

EngineName = Literal['playwright', 'seleniumbase', 'cdp_playwright']


class GroupSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=8)
    is_active: bool = True
    note: str | None = None


class GroupSourceUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    url: str | None = None
    is_active: bool | None = None
    note: str | None = None


class GroupSourceOut(BaseModel):
    id: str
    name: str
    url: str
    is_active: bool
    note: str | None
    privacy: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class KeywordCreate(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    is_active: bool = True


class KeywordOut(BaseModel):
    id: str
    keyword: str
    is_active: bool
    created_at: datetime

    model_config = {'from_attributes': True}


class ScanRequest(BaseModel):
    engine: EngineName | None = None
    group_urls: list[str] | None = None
    keywords: list[str] | None = None
    max_scrolls: int | None = Field(default=None, ge=1, le=80)
    max_posts_per_group: int | None = Field(default=None, ge=1, le=500)
    send_telegram: bool = True
    write_google_sheets: bool = True


class ScanResponse(BaseModel):
    run_id: str
    status: str
    engine: EngineName
    groups_total: int
    groups_success: int
    groups_failed: int
    posts_seen: int
    posts_inserted: int
    posts_matched: int
    errors: list[str] = []


class PostOut(BaseModel):
    id: str
    run_id: str | None
    group_url: str
    group_name: str | None
    post_id: str | None
    content_hash: str
    post_url: str | None
    author: str | None
    content: str
    matched_keywords: str | None
    engine: str
    scraped_at: datetime
    created_at: datetime

    model_config = {'from_attributes': True}


class ScanRunOut(BaseModel):
    id: str
    engine: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    groups_total: int
    groups_success: int
    groups_failed: int
    posts_seen: int
    posts_inserted: int
    posts_matched: int
    message: str | None

    model_config = {'from_attributes': True}


class ErrorLogOut(BaseModel):
    id: str
    run_id: str | None
    group_url: str | None
    engine: str | None
    error_message: str
    screenshot_path: str | None
    created_at: datetime

    model_config = {'from_attributes': True}


class SettingsOut(BaseModel):
    default_engine: EngineName
    headless: bool
    login_wait_timeout_seconds: int
    facebook_latest_sorting: bool
    max_scrolls_per_group: int
    max_posts_per_group: int
    retry_times: int
    scheduler_enabled: bool
    scheduler_interval_minutes: int
    telegram_enabled: bool
    google_sheets_enabled: bool


class LoginStatusOut(BaseModel):
    engine: EngineName
    logged_in: bool
    profile_dir: str
    storage_state_file: str | None = None


class DashboardOut(BaseModel):
    groups_total: int
    groups_active: int
    keywords_total: int
    posts_total: int
    posts_today: int
    runs_total: int
    errors_total: int
    last_run: ScanRunOut | None
    recent_posts: list[PostOut]
    recent_runs: list[ScanRunOut]
    daily_posts: list[dict[str, int | str]]
