import json
import logging
from scrapers.snapdeal_scraper import SnapdealScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

URL = "https://www.snapdeal.com/products/mobiles-mobile-phones/filters/Form_s~Smartphones"

scraper = SnapdealScraper(delay=2.0)
products = scraper.scrape(URL)

print(f"\nTotal products collected: {len(products)}")
for p in products[:5]:
    print(p)

with open("data/snapdeal_products.json", "w", encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print("\nSaved to data/snapdeal_products.json")
