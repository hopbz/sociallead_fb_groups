from pathlib import Path
from unittest.mock import Mock, patch

from app.browser.cdp_playwright_scraper import apply_stealth
from app.browser.cdp_playwright_scraper import CdpPlaywrightFacebookGroupScraper
from app.config import Settings
from app.core.group_metadata import fetch_facebook_group_metadata
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


def test_apply_stealth_supports_legacy_sync_api() -> None:
    page = Mock()
    stealth_sync = Mock()

    with patch(
        'app.browser.cdp_playwright_scraper.playwright_stealth.stealth_sync',
        stealth_sync,
        create=True,
    ):
        apply_stealth(page)

    stealth_sync.assert_called_once_with(page)


def test_group_metadata_returns_fallback_when_browser_cannot_start() -> None:
    settings = Settings(_env_file=None)

    with patch(
        'app.core.group_metadata.sync_playwright',
        side_effect=RuntimeError('browser unavailable'),
    ):
        result = fetch_facebook_group_metadata(
            ['https://www.facebook.com/groups/example'],
            settings,
        )

    assert result == {}


def test_apply_stealth_does_not_break_browser_when_legacy_api_is_incompatible() -> None:
    page = Mock()
    stealth_sync = Mock(side_effect=AttributeError('addInitScript'))

    with patch(
        'app.browser.cdp_playwright_scraper.playwright_stealth.stealth_sync',
        stealth_sync,
        create=True,
    ):
        apply_stealth(page)

    stealth_sync.assert_called_once_with(page)
