from __future__ import annotations

import logging
import shutil
import socket
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from urllib.request import urlopen
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from playwright.sync_api import Browser, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from app.browser.extractors import RawFacebookPost, make_post, pick_post_url
from app.config import Settings

logger = logging.getLogger(__name__)

ARTICLE_SELECTORS = [
    '[role="article"]',
    'div[aria-posinset]',
    'div[data-pagelet*="FeedUnit"]',
]

LOGIN_SIGNALS = [
    'login',
    'log in',
    'dang nhap',
    'đăng nhập',
    'email or phone',
    'mat khau',
    'mật khẩu',
]

LOGGED_IN_SELECTORS = [
    '[aria-label="Facebook"]',
    '[aria-label="Home"]',
    '[aria-label="Trang chủ"]',
    '[role="navigation"]',
    '[role="feed"]',
]

BLOCKED_OR_NO_ACCESS_SIGNALS = [
    "this content isn't available",
    'this content is not available',
    'content unavailable',
    "you can't access this group",
    'join group',
    'tham gia nhóm',
    'nội dung này hiện không hiển thị',
]


class CdpPlaywrightFacebookGroupScraper:
    engine = 'cdp_playwright'

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _chrome_executable(self) -> Path:
        playwright_cache = Path.home() / '.cache/ms-playwright'
        candidates = [
            shutil.which('chrome'),
            shutil.which('chrome.exe'),
            Path.home() / 'AppData/Local/Google/Chrome/Application/chrome.exe',
            Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),
            Path('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'),
            shutil.which('msedge'),
            Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'),
            *playwright_cache.glob('chromium-*/chrome-linux/chrome'),
            *playwright_cache.glob('chromium-*/chrome-linux64/chrome'),
            *playwright_cache.glob('chromium-*/chrome-win/chrome.exe'),
        ]
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return Path(candidate)
        raise RuntimeError(
            'Không tìm thấy Google Chrome hoặc Microsoft Edge. '
            'Hãy cài trình duyệt Chromium-based trước.'
        )

    def _free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('127.0.0.1', 0))
            return int(sock.getsockname()[1])

    def _wait_for_endpoint(self, endpoint_url: str) -> None:
        deadline = time.monotonic() + max(10, self.settings.cdp_reconnect_time)
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                with urlopen(f'{endpoint_url}/json/version', timeout=1):
                    return
            except Exception as exc:
                last_error = exc
                time.sleep(0.25)
        raise RuntimeError(f'Chrome CDP endpoint không sẵn sàng: {last_error}')

    @contextmanager
    def _browser_session(self, *, headed: bool) -> Iterator[str]:
        port = self._free_port()
        endpoint_url = f'http://127.0.0.1:{port}'
        args = [
            str(self._chrome_executable()),
            f'--remote-debugging-port={port}',
            f'--user-data-dir={self.settings.cdp_playwright_profile_dir.resolve()}',
            '--remote-allow-origins=*',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--lang=vi-VN',
            '--window-size=1365,850',
        ]
        if not headed:
            args.append('--headless=new')
        if self.settings.uc_mode:
            args.append('--disable-blink-features=AutomationControlled')

        creation_flags = subprocess.CREATE_NO_WINDOW if hasattr(
            subprocess,
            'CREATE_NO_WINDOW',
        ) else 0
        process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
        )
        try:
            self._wait_for_endpoint(endpoint_url)
            yield endpoint_url
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    def _connect(self, playwright, endpoint_url: str) -> Browser:
        deadline = time.monotonic() + max(1, self.settings.cdp_reconnect_time)
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                return playwright.chromium.connect_over_cdp(endpoint_url)
            except Exception as exc:
                last_error = exc
                time.sleep(0.25)
        raise RuntimeError(f'Không thể kết nối Playwright vào Chrome CDP: {last_error}')

    def _latest_group_url(self, group_url: str) -> str:
        if not self.settings.facebook_latest_sorting:
            return group_url
        parsed = urlparse(group_url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query.setdefault('sorting_setting', 'CHRONOLOGICAL')
        return urlunparse(parsed._replace(query=urlencode(query)))

    def _is_logged_in(self, page) -> bool:
        try:
            url = page.url.lower()
            body = page.locator('body').inner_text(timeout=4_000).lower()
        except Exception:
            return False
        if any(signal in url or signal in body for signal in LOGIN_SIGNALS):
            return False
        for selector in LOGGED_IN_SELECTORS:
            try:
                if page.locator(selector).count() > 0:
                    return True
            except Exception:
                continue
        return 'facebook.com' in url and bool(body.strip())

    def _page_has_no_access(self, page) -> bool:
        try:
            body = page.locator('body').inner_text(timeout=4_000).lower()
        except Exception:
            return False
        return any(signal in body for signal in BLOCKED_OR_NO_ACCESS_SIGNALS)

    def _article_cards(self, page):
        for selector in ARTICLE_SELECTORS:
            cards = page.locator(selector)
            try:
                if cards.count() > 0:
                    return cards
            except Exception:
                continue
        return page.locator('[role="article"]')

    def _extract_visible_posts(self, page, group_url: str) -> dict[str, RawFacebookPost]:
        posts: dict[str, RawFacebookPost] = {}
        cards = self._article_cards(page)
        try:
            count = min(cards.count(), 80)
        except Exception:
            return posts

        for index in range(count):
            card = cards.nth(index)
            try:
                text = card.inner_text(timeout=3_000)
                hrefs = card.locator('a[href]').evaluate_all(
                    '(elements) => elements.map(element => element.href).filter(Boolean)'
                )
                post = make_post(group_url, text, pick_post_url(hrefs), self.engine)
                if post:
                    posts[post.post_id] = post
            except Exception:
                continue
        return posts

    def login_status(self) -> dict[str, object]:
        with self._browser_session(headed=False) as endpoint_url:
            with sync_playwright() as playwright:
                browser = self._connect(playwright, endpoint_url)
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(
                    'https://www.facebook.com/',
                    wait_until='domcontentloaded',
                    timeout=self.settings.page_load_timeout_ms,
                )
                page.wait_for_timeout(1_500)
                return {
                    'logged_in': self._is_logged_in(page),
                    'profile_dir': str(self.settings.cdp_playwright_profile_dir),
                    'storage_state_file': None,
                }

    def ensure_login(self) -> None:
        logger.info('Opening CDP Playwright browser for manual Facebook login')
        deadline = time.monotonic() + self.settings.login_wait_timeout_seconds
        with self._browser_session(headed=True) as endpoint_url:
            with sync_playwright() as playwright:
                browser = self._connect(playwright, endpoint_url)
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(
                    'https://www.facebook.com/',
                    wait_until='domcontentloaded',
                    timeout=self.settings.page_load_timeout_ms,
                )
                while time.monotonic() < deadline:
                    page.wait_for_timeout(2_500)
                    if self._is_logged_in(page):
                        logger.info('Facebook login detected in CDP Playwright profile')
                        return
                raise TimeoutError(
                    f'Chưa phát hiện đăng nhập Facebook sau '
                    f'{self.settings.login_wait_timeout_seconds} giây.'
                )

    def scrape_group(
        self,
        group_url: str,
        max_scrolls: int,
        max_posts: int,
        screenshot_dir: Path,
    ) -> list[RawFacebookPost]:
        posts: dict[str, RawFacebookPost] = {}
        with self._browser_session(
            headed=not self.settings.headless,
        ) as endpoint_url:
            with sync_playwright() as playwright:
                browser = self._connect(playwright, endpoint_url)
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()
                page.set_default_timeout(self.settings.page_load_timeout_ms)
                try:
                    page.goto(
                        self._latest_group_url(group_url),
                        wait_until='domcontentloaded',
                        timeout=self.settings.page_load_timeout_ms,
                    )
                    page.wait_for_timeout(4_500)
                    if not self._is_logged_in(page):
                        raise RuntimeError(
                            'Facebook profile cdp_playwright chưa đăng nhập hoặc session đã hết hạn.'
                        )
                    if self._page_has_no_access(page):
                        raise RuntimeError(
                            'Tài khoản chưa có quyền xem group hoặc group yêu cầu tham gia/phê duyệt.'
                        )

                    idle_rounds = 0
                    for _ in range(max_scrolls):
                        try:
                            page.wait_for_selector(','.join(ARTICLE_SELECTORS), timeout=15_000)
                        except PlaywrightTimeoutError:
                            logger.info('No article cards visible yet for %s', group_url)

                        before_count = len(posts)
                        posts.update(self._extract_visible_posts(page, group_url))
                        if len(posts) >= max_posts:
                            break

                        idle_rounds = idle_rounds + 1 if len(posts) == before_count else 0
                        if idle_rounds >= 2:
                            break

                        page.mouse.wheel(0, 2_600)
                        page.wait_for_timeout(int(self.settings.scroll_wait_seconds * 1_000))

                    return list(posts.values())[:max_posts]
                except Exception:
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    screenshot = screenshot_dir / f'cdp_playwright_error_{abs(hash(group_url))}.png'
                    try:
                        page.screenshot(path=str(screenshot), full_page=True)
                    except Exception:
                        pass
                    raise
