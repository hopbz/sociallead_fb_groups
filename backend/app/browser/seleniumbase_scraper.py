from __future__ import annotations

import logging
from pathlib import Path

from seleniumbase import SB

from app.browser.extractors import RawFacebookPost, make_post, pick_post_url
from app.config import Settings

logger = logging.getLogger(__name__)


class SeleniumBaseFacebookGroupScraper:
    engine = 'seleniumbase'

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _sb_context(self, headed: bool = True):
        """Trả về SB context với UC Mode + stealth settings."""
        return SB(
            uc=self.settings.uc_mode,
            browser='chrome',
            headed=headed,
            user_data_dir=str(self.settings.seleniumbase_profile_dir),
            locale_code='vi',
            # Human-like delays
            slow=False,
        )

    def ensure_login(self) -> None:
        logger.info('Opening SeleniumBase (UC Mode) for Facebook login')
        with self._sb_context(headed=True) as sb:
            sb.uc_open_with_reconnect('https://www.facebook.com/', reconnect_time=3)
            print('\n[LOGIN] Đăng nhập Facebook trong cửa sổ vừa mở.')
            input('Nhấn Enter sau khi đăng nhập thành công... ')

    def _login_required(self, sb) -> bool:
        try:
            url = sb.get_current_url().lower()
            body = sb.get_text('body').lower()
        except Exception:
            return False
        signals = ['login', 'log in', 'đăng nhập', 'email or phone', 'mật khẩu']
        return any(s in url or s in body for s in signals)

    def scrape_group(
        self,
        group_url: str,
        max_scrolls: int,
        max_posts: int,
        screenshot_dir: Path,
    ) -> list[RawFacebookPost]:
        posts: dict[str, RawFacebookPost] = {}

        with self._sb_context(headed=not self.settings.headless) as sb:
            try:
                # CDP-style open: navigate rồi reconnect sau N giây
                sb.uc_open_with_reconnect(
                    group_url,
                    reconnect_time=self.settings.cdp_reconnect_time,
                )

                # Xử lý CAPTCHA nếu có
                try:
                    sb.uc_gui_handle_captcha()
                except Exception:
                    pass

                sb.sleep(3)

                if self._login_required(sb):
                    raise RuntimeError(
                        'Facebook session hết hạn. Chạy ensure_login() trước.'
                    )

                for _ in range(max_scrolls):
                    # Check và bypass captcha mỗi vòng lặp
                    try:
                        sb.uc_gui_handle_captcha()
                    except Exception:
                        pass

                    try:
                        sb.wait_for_element_present('[role="article"]', timeout=15)
                    except Exception:
                        logger.warning('No article cards for %s', group_url)

                    cards = sb.find_elements('[role="article"]')
                    for card in cards:
                        if len(posts) >= max_posts:
                            break
                        try:
                            text = card.text
                            links = card.find_elements('css selector', 'a[href]')
                            hrefs = [
                                a.get_attribute('href') for a in links
                                if a.get_attribute('href')
                            ]
                            post_url = pick_post_url(hrefs)
                            post = make_post(group_url, text, post_url, self.engine)
                            if post:
                                posts[post.post_id] = post
                        except Exception:
                            continue

                    if len(posts) >= max_posts:
                        break

                    # Scroll tự nhiên hơn
                    sb.execute_script(
                        "window.scrollBy({top: window.innerHeight * 0.85, behavior: 'smooth'});"
                    )
                    sb.sleep(self.settings.scroll_wait_seconds)

                return list(posts.values())[:max_posts]

            except Exception:
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                shot = screenshot_dir / f'sb_error_{abs(hash(group_url))}.png'
                try:
                    sb.save_screenshot(str(shot))
                except Exception:
                    pass
                raise