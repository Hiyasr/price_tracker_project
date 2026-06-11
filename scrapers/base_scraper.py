import time
import logging
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    def __init__(self, delay=2.0):
        self.delay = delay
        self.driver = None

    def start_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        logger.info("Browser started")

    def stop_driver(self):
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

    def wait(self):
        time.sleep(self.delay)

    @abstractmethod
    def scrape(self, url: str) -> list:
        pass