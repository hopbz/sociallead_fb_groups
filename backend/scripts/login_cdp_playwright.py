from app.browser.cdp_playwright_scraper import CdpPlaywrightFacebookGroupScraper
from app.config import get_settings


def main() -> None:
    settings = get_settings()
    scraper = CdpPlaywrightFacebookGroupScraper(settings)
    scraper.ensure_login()
    print('OK: CDP Playwright Facebook profile đã đăng nhập.')


if __name__ == '__main__':
    main()
