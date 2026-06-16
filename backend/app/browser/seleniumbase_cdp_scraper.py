from __future__ import annotations

import logging
import random
import time
from pathlib import Path

from seleniumbase import SB

from app.browser.extractors import RawFacebookPost, make_post, pick_post_url
from app.config import Settings

logger = logging.getLogger(__name__)


class SeleniumBaseCDPScraper:
    engine = "seleniumbase_cdp"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.sb = None

    def start(self):
        self.sb = SB(
            uc=True,                    # Undetected Chrome
            headless=self.settings.headless,
            user_data_dir=str(self.settings.cdp_playwright_profile_dir),
            locale="vi-VN",
            ad_block=True,
            block_images=False,
            disable_csp=True,
            window_size="1920,1080",
            undetectable=True,
        )
        self.sb.activate_cdp_mode()     # CDP Mode mạnh nhất
        return self.sb

    def login_status(self) -> dict:
        sb = self.start()
        try:
            sb.open("https://www.facebook.com/")
            time.sleep(4)
            logged_in = sb.is_element_visible('[role="feed"]') or sb.is_element_visible('[aria-label="Facebook"]')
            return {"logged_in": logged_in, "engine": self.engine}
        finally:
            sb.quit()

    def ensure_login(self):
        logger.info("Mở SeleniumBase để login...")
        sb = SB(uc=True, headless=False, user_data_dir=str(self.settings.cdp_playwright_profile_dir))
        sb.activate_cdp_mode()
        sb.open("https://www.facebook.com/")
        input("Login xong nhấn Enter...")
        sb.quit()

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

        self.sb = self.start()
        try:
            self.sb.open(group_url)
            self.sb.sleep(5)

            for i in range(max_scrolls):
                # Human-like actions
                self.sb.execute_script("window.scrollBy(0, 1100 + Math.random()*1100);")
                self.sb.sleep(random.uniform(2.5, 5.0))
                
                if random.random() > 0.45:
                    self.sb.move_mouse(random.randint(400, 1400), random.randint(200, 800))

                articles = self.sb.find_elements("div[role='article']")
                for article in articles:
                    try:
                        text = article.text.strip()
                        post = make_post(group_url, text, group_url, self.engine)
                        if post and post.post_id not in posts:
                            posts[post.post_id] = post
                            if len(posts) >= max_posts:
                                return list(posts.values())
                    except:
                        continue

                logger.info(f"[SeleniumBase CDP] Scroll {i+1}/{max_scrolls} | Posts: {len(posts)}")

            return list(posts.values())[:max_posts]

        except Exception as e:
            logger.error(f"Lỗi: {e}")
            self.sb.save_screenshot(str(screenshot_dir / f"cdp_error_{int(time.time())}.png"))
            raise
        finally:
            if self.sb:
                self.sb.quit()