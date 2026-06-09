from pathlib import Path
from unittest.mock import patch

from app.browser.cdp_playwright_scraper import CdpPlaywrightFacebookGroupScraper
from app.config import Settings
from app.core.scanner import FacebookGroupScanner
from app.schemas import ScanRequest


def test_settings_create_cdp_profile_directory() -> None:
    root = Path('test-data')
    settings = Settings(
        _env_file=None,
        playwright_profile_dir=root / 'playwright',
        playwright_storage_state_file=root / 'playwright/state.json',
        seleniumbase_profile_dir=root / 'seleniumbase',
        cdp_playwright_profile_dir=root / 'cdp_playwright',
        screenshot_dir=root / 'screenshots',
        log_file=root / 'logs/app.log',
        csv_output_file=root / 'output/posts.csv',
    )

    with patch.object(Path, 'mkdir') as mkdir:
        settings.ensure_dirs()

    assert mkdir.call_count == 7
    mkdir.assert_any_call(parents=True, exist_ok=True)


def test_scan_request_accepts_cdp_playwright() -> None:
    request = ScanRequest(engine='cdp_playwright')

    assert request.engine == 'cdp_playwright'


def test_scanner_routes_cdp_playwright_engine() -> None:
    scanner = FacebookGroupScanner(Settings(_env_file=None), db=None)  # type: ignore[arg-type]

    scraper = scanner._scraper('cdp_playwright')

    assert isinstance(scraper, CdpPlaywrightFacebookGroupScraper)
