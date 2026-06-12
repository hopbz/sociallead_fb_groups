# backend/app/browser/seleniumbase_cdp_scraper.py
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

    def __init__(self, settings: Settings) -> None:
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
            disable_automation_controlled=self.settings.disable_automation_controlled,
            no_sandbox=True,
            disable_gpu=True,
            disable_dev_shm_usage=True,
            agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.37",
        )
        self.sb.activate_cdp_mode()
        return self.sb

    def login_status(self) -> dict:
        sb = self.start()
        try:
            sb.open("https://www.facebook.com/")
            time.sleep(3)
            logged_in = any([
                sb.is_element_visible('[aria-label="Facebook"]'),
                sb.is_element_visible('[role="feed"]')
            ])
            return {"logged_in": logged_in, "engine": self.engine}
        finally:
            sb.quit()

    def ensure_login(self):
        logger.info("Mở SeleniumBase CDP để đăng nhập thủ công...")
        sb = SB(uc=True, headless=False, user_data_dir=str(self.settings.cdp_playwright_profile_dir))
        sb.activate_cdp_mode()
        sb.open("https://www.facebook.com/")
        # Patch thêm để tránh bị phát hiện
        sb.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['vi-VN', 'vi', 'en']});
            window.chrome = { runtime: {} };
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        input("✅ Đã login xong? Nhấn Enter để lưu profile...")
        sb.quit()

    def scrape_group(
        self,
        group_url: str,
        max_scrolls: int = 15,
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
            # Patch thêm sau khi mở trang
            self.sb.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['vi-VN', 'vi', 'en']});
                window.chrome = { runtime: {} };
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """)

            for i in range(max_scrolls):
                # Cuộn mượt + delay ngẫu nhiên
                scroll_dist = random.randint(600, 1500)
                self.sb.execute_script(f"window.scrollBy({{top: {scroll_dist}, behavior: 'smooth'}});")
                delay = random.uniform(3.0, 5.0)
                time.sleep(delay)

                # Di chuyển chuột giả lập
                self.sb.execute_script("""
                    var event = new MouseEvent('mousemove', {
                        clientX: Math.random() * window.innerWidth,
                        clientY: Math.random() * window.innerHeight
                    });
                    document.dispatchEvent(event);
                """)

                articles = self.sb.find_elements("div[role='article']")
                for article in articles:
                    try:
                        text = article.text.strip()
                        post = make_post(group_url, text, group_url, self.engine)
                        if post and post.post_id not in posts:
                            posts[post.post_id] = post
                            if len(posts) >= max_posts:
                                return list(posts.values())
                    except Exception:
                        continue

                logger.info(f"Scroll {i+1}/{max_scrolls} - Posts: {len(posts)}")

            return list(posts.values())[:max_posts]

        except Exception as e:
            logger.error(f"Lỗi: {e}")
            try:
                self.sb.save_screenshot(str(screenshot_dir / f"cdp_error_{int(time.time())}.png"))
            except Exception:
                pass
            raise
        finally:
            if self.sb:
                self.sb.quit()