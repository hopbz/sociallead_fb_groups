from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

EngineName = Literal['playwright', 'seleniumbase', 'cdp_playwright']


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'SocialLead Facebook Groups Backend'
    env: str = 'local'
    api_token: str = 'change-this-token'
    database_url: str = 'sqlite:///./data/sociallead_local.db'
    cors_origins: str = 'http://localhost:3000,http://127.0.0.1:3000'

    default_engine: EngineName = 'playwright'
    headless: bool = False
    browser_slow_mo_ms: int = 80
    page_load_timeout_ms: int = 45_000
    scroll_wait_seconds: float = 2.5
    max_scrolls_per_group: int = 8
    max_posts_per_group: int = 50
    retry_times: int = 2
    retry_sleep_seconds: float = 3
    login_wait_timeout_seconds: int = 300
    facebook_latest_sorting: bool = True
    uc_mode: bool = True
    cdp_reconnect_time: int = 3

    playwright_profile_dir: Path = Path('data/profiles/playwright_fb')
    playwright_storage_state_file: Path = Path('data/profiles/playwright_fb/storage_state.json')
    seleniumbase_profile_dir: Path = Path('data/profiles/seleniumbase_fb')
    cdp_playwright_profile_dir: Path = Path('data/profiles/cdp_playwright_fb')
    screenshot_dir: Path = Path('data/screenshots')
    log_file: Path = Path('data/logs/app.log')
    csv_output_file: Path = Path('data/output/facebook_group_posts.csv')

    telegram_enabled: bool = False
    telegram_bot_token: str = ''
    telegram_chat_id: str = ''

    google_sheets_enabled: bool = False
    google_sheets_spreadsheet_id: str = ''
    google_sheets_worksheet_name: str = 'Facebook Group Posts'
    google_service_account_json: Path = Path('data/service_account.json')

    scheduler_enabled: bool = False
    scheduler_interval_minutes: int = 30

    def cors_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(',') if item.strip()]

    def ensure_dirs(self) -> None:
        for path in [
            self.playwright_profile_dir,
            self.playwright_storage_state_file.parent,
            self.seleniumbase_profile_dir,
            self.cdp_playwright_profile_dir,
            self.screenshot_dir,
            self.log_file.parent,
            self.csv_output_file.parent,
        ]:
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
