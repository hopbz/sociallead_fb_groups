from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from typing import List

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth as _stealth_apply  # playwright_stealth >= 1.0

# Compat shim: phiên bản cũ dùng stealth_sync, phiên bản mới dùng stealth()
def stealth_sync(page):  # type: ignore[override]
    _stealth_apply(page)


from app.browser.extractors import RawFacebookPost, make_post, pick_post_url
from app.config import Settings

logger = logging.getLogger(__name__)


class PlaywrightStealthScraper:
    engine = "playwright_stealth"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _human_mouse_move(self, page, target_x: int, target_y: int):
        """Di chuyển chuột theo đường cong tự nhiên"""
        steps = random.randint(28, 45)
        for i in range(steps):
            progress = i / steps
            x = target_x * progress + random.uniform(-12, 12)
            y = target_y * (progress ** 1.8) + random.uniform(-10, 10)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.008, 0.028))

    def _human_scroll(self, page):
        for _ in range(random.randint(2, 4)):
            page.mouse.wheel(0, random.randint(900, 1900))
            time.sleep(random.uniform(0.7, 1.9))
            if random.random() < 0.35:
                self._human_mouse_move(page, random.randint(400, 1300), random.randint(200, 800))

    def login_status(self) -> dict:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            context = browser.new_context(viewport={"width": 1920, "height": 1080}, locale="vi-VN")
            page = context.new_page()
            stealth_sync(page)
            page.goto("https://www.facebook.com/", timeout=30000)
            time.sleep(3)
            logged_in = any([page.locator(s).count() > 0 for s in ['[role="feed"]', '[aria-label="Facebook"]']])
            browser.close()
            return {"logged_in": logged_in, "engine": self.engine}

    def ensure_login(self):
        logger.info("Mở browser để login thủ công...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=['--no-sandbox', '--window-size=1365,850'])
            context = browser.new_context(locale="vi-VN")
            page = context.new_page()
            stealth_sync(page)
            page.goto("https://www.facebook.com/")
            input("Đăng nhập xong thì nhấn Enter...")
            browser.close()

    def scrape_group(
        self,
        group_url: str,
        max_scrolls: int = 12,
        max_posts: int = 50,
        screenshot_dir: Path | None = None,
    ) -> list[RawFacebookPost]:
        posts: dict[str, RawFacebookPost] = {}
        screenshot_dir = screenshot_dir or Path("data/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.settings.headless,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled', '--window-size=1920,1080']
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="vi-VN",
                timezone_id="Asia/Ho_Chi_Minh",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            stealth_sync(page)

            # Extra fingerprint patch
            page.add_init_script("""
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
                Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            """)

            try:
                page.goto(group_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)

                for scroll in range(max_scrolls):
                    self._human_scroll(page)
                    time.sleep(random.uniform(2.8, 5.2))

                    cards = page.locator('[role="article"]').all()
                    for card in cards:
                        try:
                            text = card.inner_text(timeout=3000)
                            hrefs = card.locator('a[href]').evaluate_all("(els) => els.map(el => el.href).filter(Boolean)")
                            post = make_post(group_url, text, pick_post_url(hrefs), self.engine)
                            if post and post.post_id not in posts:
                                posts[post.post_id] = post
                                if len(posts) >= max_posts:
                                    return list(posts.values())
                        except:
                            continue

                    logger.info(f"[Playwright Stealth] Scroll {scroll+1}/{max_scrolls} | Posts: {len(posts)}")

                return list(posts.values())[:max_posts]

            except Exception as e:
                logger.error(f"Lỗi scrape: {e}")
                page.screenshot(path=str(screenshot_dir / f"stealth_error_{int(time.time())}.png"))
                raise
            finally:
                browser.close()