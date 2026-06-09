from app.config import get_settings
from app.browser.playwright_scraper import PlaywrightFacebookGroupScraper

if __name__ == '__main__':
    PlaywrightFacebookGroupScraper(get_settings()).ensure_login()
