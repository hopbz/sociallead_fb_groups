from app.config import get_settings
from app.browser.seleniumbase_scraper import SeleniumBaseFacebookGroupScraper

if __name__ == '__main__':
    SeleniumBaseFacebookGroupScraper(get_settings()).ensure_login()
