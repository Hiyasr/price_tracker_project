import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SnapdealScraper(BaseScraper):
    def __init__(self, delay=2.0):
        super().__init__(delay)
        self.source = "snapdeal"

    def scroll_to_bottom(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def parse_products(self):
        products = []

        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-tuple-listing"))
            )
        except Exception:
            logger.error("Product cards never loaded")
            return products

        cards = self.driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")
        logger.info(f"Found {len(cards)} product cards")

        for card in cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, "p.product-title").text.strip()

                try:
                    price = card.find_element(By.CSS_SELECTOR, "span.product-price").text.strip()
                except:
                    price = None

                try:
                    mrp = card.find_element(By.CSS_SELECTOR, "span.product-desc-price").text.strip()
                except:
                    mrp = None

                try:
                    discount = card.find_element(By.CSS_SELECTOR, "div.product-discount span").text.strip()
                except:
                    discount = None

                try:
                    rating_style = card.find_element(By.CSS_SELECTOR, "div.filled-stars").get_attribute("style")
                    rating = rating_style.replace("width:", "").replace("%", "").strip()
                except:
                    rating = None

                try:
                    url = card.find_element(By.CSS_SELECTOR, "a.dp-widget-link").get_attribute("href")
                except:
                    url = None

                if name and price:
                    products.append({
                        "name": name,
                        "price": price,
                        "mrp": mrp,
                        "discount": discount,
                        "rating": rating,
                        "availability": "in_stock",
                        "url": url,
                        "source": self.source
                    })

            except Exception as e:
                logger.warning(f"Skipped a product: {e}")
                continue

        return products

    def scrape(self, url: str) -> list:
        logger.info(f"Scraping: {url}")
        self.start_driver()

        try:
            self.driver.get(url)
            time.sleep(6)
            self.scroll_to_bottom()
            products = self.parse_products()
            logger.info(f"Collected {len(products)} products")
            return products
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return []
        finally:
            self.stop_driver()