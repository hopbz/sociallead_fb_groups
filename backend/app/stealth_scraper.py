# backend/app/stealth_scraper.py
"""
FacebookStealthScraper — scraper stealth dùng SeleniumBase + CDP.
Hỗ trợ: đăng nhập, thu thập bài viết, trích xuất SĐT, lấy member ID,
tự động đăng bài (không khuyến khích dùng trong production).
"""
from __future__ import annotations

import os
import re
import time
import random
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from .config import Config
from .proxy_manager import ProxyManager
from .captcha_solver import UltimateCaptchaSolver


# ─────────────────────────────────────────────────────────────────────────────
class FacebookStealthScraper:
    """Scraper chống phát hiện cho Facebook Groups."""

    CHROME_ARGS: List[str] = [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--disable-popup-blocking",
        "--disable-notifications",
        "--lang=en-US",
    ]

    def __init__(
        self,
        profile_dir: Optional[str] = None,
        proxy: Optional[str] = None,
    ) -> None:
        self.profile_dir: str = profile_dir or Config.PROFILE_DIR
        self.proxy: Optional[str] = proxy
        self.driver: Any = None
        self.is_logged_in: bool = False
        self.captcha_solver: Optional[UltimateCaptchaSolver] = None
        self.proxy_manager = ProxyManager(Config.PROXY_LIST)

    # ── Khởi tạo driver ──────────────────────────────────────────────────────
    def init_driver(self, headless: bool = False, use_cdp: bool = True) -> Any:
        """Khởi tạo SeleniumBase Driver với chế độ anti-detection."""
        from seleniumbase import Driver  # lazy import

        if not self.proxy and self.proxy_manager.proxy_list:
            self.proxy = self.proxy_manager.get_random_proxy()

        chrome_args = list(self.CHROME_ARGS)
        if self.proxy:
            chrome_args.append(f"--proxy-server={self.proxy}")

        os.makedirs(self.profile_dir, exist_ok=True)

        if use_cdp:
            self.driver = Driver(
                browser="chrome",
                uc=True,
                headless=headless,
                user_data_dir=self.profile_dir,
                disable_csp=True,
                agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
                ),
                chromium_arg=",".join(chrome_args),
            )
        else:
            # Fallback: dùng UC mode bình thường
            self.driver = Driver(
                browser="chrome",
                uc=True,
                headless=headless,
                user_data_dir=self.profile_dir,
            )

        # Kích thước cửa sổ ngẫu nhiên
        w = random.choice([1366, 1440, 1536, 1920])
        h = random.choice([768, 900, 864, 1080])
        self.driver.set_window_size(w, h)

        self.captcha_solver = UltimateCaptchaSolver(self.driver)
        print(f"[Driver] Khởi tạo xong — proxy={self.proxy}, size={w}x{h}")
        return self.driver

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _random_delay(self, min_ms: int = 100, max_ms: int = 300) -> None:
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

    def _human_like_typing(self, element: Any, text: str) -> None:
        for char in text:
            element.send_keys(char)
            self._random_delay(
                Config.TYPING_DELAY_MIN,
                Config.TYPING_DELAY_MAX,
            )

    # ── Đăng nhập ────────────────────────────────────────────────────────────
    def _check_logged_in(self) -> bool:
        try:
            self.driver.get("https://www.facebook.com/")
            self._random_delay(2000, 3000)
            indicators = [
                "//div[@aria-label='Facebook']//span[contains(text(),'Home')]",
                "//a[@aria-label='Profile']",
            ]
            for xp in indicators:
                if self.driver.find_elements(By.XPATH, xp):
                    self.is_logged_in = True
                    return True
            return False
        except Exception as exc:
            print(f"[Login check] Lỗi: {exc}")
            return False

    def login_facebook(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> bool:
        if self._check_logged_in():
            print("[Login] Đã đăng nhập qua session.")
            return True

        if not email or not password:
            print("[Login] Không có thông tin đăng nhập — thử tải session...")
            self.driver.get("https://www.facebook.com/")
            time.sleep(3)
            return self._check_logged_in()

        self.driver.get("https://www.facebook.com/login")
        self._random_delay(2000, 4000)
        try:
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.click()
            self._human_like_typing(email_input, email)

            pass_input = self.driver.find_element(By.ID, "pass")
            self._human_like_typing(pass_input, password)

            self.driver.find_element(By.NAME, "login").click()
            time.sleep(5)

            if self._check_captcha():
                print("[Login] Phát hiện CAPTCHA, đang giải...")
                assert self.captcha_solver is not None
                ok, msg = self.captcha_solver.solve_captcha()
                if ok:
                    print(f"[Login] {msg}")
                elif not self.captcha_solver.solve_with_seleniumbase():
                    print("[Login] Không giải được CAPTCHA.")
                    return False

            WebDriverWait(self.driver, 30).until(
                lambda d: "facebook.com" in d.current_url
                and "/login" not in d.current_url
            )
            self.is_logged_in = True
            print("[Login] Thành công.")
            return True
        except Exception as exc:
            print(f"[Login] Lỗi: {exc}")
            return False

    def _check_captcha(self) -> bool:
        src = self.driver.page_source.lower()
        return any(k in src for k in ("recaptcha", "hcaptcha", "captcha"))

    def _check_checkpoint(self) -> bool:
        src = self.driver.page_source.lower()
        return any(k in src for k in ("checkpoint", "verify your identity", "security check"))

    # ── Thu thập bài viết ────────────────────────────────────────────────────
    def scrape_group_posts(
        self,
        group_url: str,
        max_posts: int = 50,
    ) -> List[Dict[str, Any]]:
        if not self.is_logged_in:
            print("[Scrape] Chưa đăng nhập.")
            return []

        self.driver.get(group_url)
        self._random_delay(3000, 5000)

        posts: List[Dict[str, Any]] = []
        seen_ids: set[str] = set()
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        stale_count = 0

        while len(posts) < max_posts and stale_count < 5:
            target_y = (
                self.driver.execute_script("return window.pageYOffset")
                + random.randint(300, 800)
            )
            self.driver.execute_script(
                f"window.scrollTo({{top:{target_y},behavior:'smooth'}});"
            )
            self._random_delay(1500, 3000)

            # Random mouse move để tránh bot detection
            if random.random() > 0.7:
                try:
                    ActionChains(self.driver).move_by_offset(
                        random.randint(-100, 100), random.randint(-100, 100)
                    ).perform()
                except Exception:
                    pass

            # Lấy phần tử bài viết
            post_elements = self.driver.find_elements(By.XPATH, "//div[@role='article']")
            for elem in post_elements:
                try:
                    data = self._extract_post_data(elem)
                    pid = data.get("id") or data.get("content", "")[:60]
                    if data and pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        posts.append(data)
                        print(f"[Scrape] Bài {len(posts)}: {data.get('content','')[:60]}…")
                except Exception:
                    pass

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                stale_count += 1
            else:
                stale_count = 0
            last_height = new_height

        print(f"[Scrape] Tổng {len(posts)} bài viết.")
        return posts

    def _extract_post_data(self, post_element: Any) -> Dict[str, Any]:
        try:
            post_id: str = post_element.get_attribute("data-ft") or ""

            content_elems = post_element.find_elements(
                By.XPATH, ".//div[@data-ad-comet-preview='message']"
            )
            content = content_elems[0].text if content_elems else ""

            author_elems = post_element.find_elements(
                By.XPATH,
                ".//a[contains(@href,'/user/') or contains(@href,'/profile.php')]",
            )
            author_name = author_elems[0].text if author_elems else ""
            author_url = author_elems[0].get_attribute("href") if author_elems else ""

            time_elems = post_element.find_elements(By.TAG_NAME, "time")
            timestamp = time_elems[0].get_attribute("datetime") if time_elems else None

            return {
                "id": post_id,
                "content": content,
                "author_name": author_name,
                "author_url": author_url,
                "timestamp": timestamp,
                "url": self.driver.current_url,
            }
        except Exception:
            return {}

    # ── Trích xuất SĐT từ profile ────────────────────────────────────────────
    def extract_profile_phone(self, profile_url: str) -> Optional[str]:
        if not self.is_logged_in:
            return None
        self.driver.get(profile_url)
        self._random_delay(2000, 4000)
        page_text: str = self.driver.page_source
        patterns = [
            r"\+?\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}",
            r"phone[\s]*:[\s]*([\+\d\s\-\(\)]+)",
            r"tel:([\+\d]+)",
        ]
        for pat in patterns:
            for match in re.findall(pat, page_text, re.IGNORECASE):
                raw = match[0] if isinstance(match, tuple) else match
                cleaned = re.sub(r"[^\d\+]", "", raw)
                if 10 <= len(cleaned) <= 15:
                    return cleaned
        return None

    # ── Lấy member IDs ───────────────────────────────────────────────────────
    def extract_group_member_ids(
        self,
        group_url: str,
        limit: int = 100,
    ) -> List[str]:
        if not self.is_logged_in:
            return []
        self.driver.get(f"{group_url.rstrip('/')}/members")
        self._random_delay(3000, 5000)
        ids: List[str] = []
        last_count = -1

        while len(ids) < limit and len(ids) != last_count:
            last_count = len(ids)
            links = self.driver.find_elements(
                By.XPATH,
                "//a[contains(@href,'/profile.php') or contains(@href,'/user/')]",
            )
            for link in links:
                href: str = link.get_attribute("href") or ""
                if "facebook.com" not in href:
                    continue
                m = re.search(r"id=(\d+)", href) or re.search(r"/user/(\d+)", href)
                if m and m.group(1) not in ids:
                    ids.append(m.group(1))
            self.driver.execute_script("window.scrollBy(0,800);")
            self._random_delay(2000, 3000)

        print(f"[Members] Trích xuất {len(ids)} ID thành viên.")
        return ids

    # ── Tự động đăng bài ─────────────────────────────────────────────────────
    def auto_post_to_group(
        self,
        group_url: str,
        content: str,
        image_path: Optional[str] = None,
    ) -> bool:
        """⚠️  Chú ý: tính năng này vi phạm TOS của Facebook — chỉ dùng nghiên cứu."""
        if not self.is_logged_in:
            return False
        self.driver.get(group_url)
        self._random_delay(3000, 5000)
        try:
            create_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='button' and contains(text(),'Write')]")
                )
            )
            create_btn.click()
            self._random_delay(1000, 2000)

            post_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@role='textbox' and @aria-label]")
                )
            )
            post_input.click()
            self._human_like_typing(post_input, content)
            self._random_delay(500, 1000)

            if image_path and os.path.exists(image_path):
                file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
                file_input.send_keys(os.path.abspath(image_path))
                self._random_delay(2000, 4000)

            post_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@aria-label='Post' and @role='button']")
                )
            )
            post_btn.click()
            print("[AutoPost] Thành công.")
            return True
        except Exception as exc:
            print(f"[AutoPost] Lỗi: {exc}")
            return False

    # ── Đóng driver ──────────────────────────────────────────────────────────
    def close(self) -> None:
        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
