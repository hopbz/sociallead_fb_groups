from __future__ import annotations

import os
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

    default_engine: EngineName = 'cdp_playwright'  # nên dùng cdp_playwright để anti-detection tốt nhất
    headless: bool = False
    browser_slow_mo_ms: int = 120          # tăng lên để chậm hơn, tránh bị phát hiện
    page_load_timeout_ms: int = 60_000
    scroll_wait_seconds: float = 3.5       # chờ lâu hơn
    max_scrolls_per_group: int = 8
    max_posts_per_group: int = 30
    retry_times: int = 2
    retry_sleep_seconds: float = 3
    login_wait_timeout_seconds: int = 300
    facebook_latest_sorting: bool = True
    uc_mode: bool = True
    cdp_reconnect_time: int = 3
    cdp_chrome_executable: str = ''
    browser_login_url: str = ''

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

    lead_score_threshold: int = 7
    lead_niche_name: str = 'Dịch vụ địa phương'
    lead_positive_keywords: str = 'cần tìm, tư vấn, báo giá, recommend, looking for'
    lead_negative_keywords: str = 'đã mua, không cần, spam'
    lead_comment_tone: str = 'Tự nhiên, hữu ích, lịch sự và không thúc ép inbox.'
    lead_max_posts_per_group: int = 50
    lead_scan_interval_minutes: int = 30

    google_sheets_enabled: bool = False
    google_sheets_spreadsheet_id: str = ''
    google_sheets_worksheet_name: str = 'Facebook Group Posts'
    google_service_account_json: Path = Path('data/service_account.json')

    scheduler_enabled: bool = False
    scheduler_interval_minutes: int = 30

    # ========== CẤU HÌNH ANTI-DETECTION MỚI ==========
    disable_automation_controlled: bool = True   # cho SeleniumBase
    human_like_mouse_movement: bool = True
    scroll_smooth: bool = True
    min_scroll_delay_ms: int = 800
    max_scroll_delay_ms: int = 2000

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


class Config:
    """
    Cấu hình bổ sung cho stealth scraper — đọc từ biến môi trường.
    Tách riêng khỏi Settings để không ảnh hưởng tới FastAPI app.
    """

    # Facebook credentials (để tự động login nếu chưa có session)
    FB_EMAIL: str = os.environ.get('FB_EMAIL', '')
    FB_PASSWORD: str = os.environ.get('FB_PASSWORD', '')

    # CAPTCHA solver API keys (để trống nếu không dùng dịch vụ trả phí)
    TWOCAPTCHA_API_KEY: str = os.environ.get('TWOCAPTCHA_API_KEY', '')
    CAPSOLVER_API_KEY: str = os.environ.get('CAPSOLVER_API_KEY', '')

    # Proxy list — cách nhau bằng dấu phẩy
    PROXY_LIST: list[str] = [
        p.strip()
        for p in os.environ.get('PROXY_LIST', '').split(',')
        if p.strip()
    ]

    # Headless mode (khuyến cáo False khi debug)
    HEADLESS: bool = os.environ.get('HEADLESS', 'false').lower() == 'true'

    # Thư mục lưu profile browser
    PROFILE_DIR: str = os.environ.get('PROFILE_DIR', 'browser_profiles')

    # Delay gõ phím (milliseconds)
    TYPING_DELAY_MIN: int = 50
    TYPING_DELAY_MAX: int = 200

    # Delay cuộn trang (milliseconds)
    SCROLL_DELAY_MIN: int = 800
    SCROLL_DELAY_MAX: int = 2500
