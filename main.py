import json
import logging
from scrapers.snapdeal_scraper import SnapdealScraper
from database.db import save_products

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

CATEGORIES = [
    {
        "name": "smartphones",
        "url": "https://www.snapdeal.com/products/mobiles-mobile-phones/filters/Form_s~Smartphones"
    },
    {
        "name": "laptops",
        "url": "https://www.snapdeal.com/products/computers-laptops"
    },
    {
        "name": "earphones",
        "url": "https://www.snapdeal.com/products/mobiles-headphones-earphones"
    },
    {
        "name": "tablets",
        "url": "https://www.snapdeal.com/products/mobiles-tablets"
    },
]

all_products = []
scraper = SnapdealScraper(delay=2.0)

for category in CATEGORIES:
    print(f"\n--- Scraping: {category['name']} ---")
    products = scraper.scrape(category["url"])
    for p in products:
        p["category"] = category["name"]
    all_products.extend(products)
    print(f"Collected {len(products)} products from {category['name']}")

print(f"\nTotal products collected: {len(all_products)}")

# Save to JSON
with open("data/snapdeal_products.json", "w", encoding="utf-8") as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)
print("Saved to data/snapdeal_products.json")

# Save to database
print("\nSaving to database...")
products_saved, prices_saved = save_products(all_products)
print(f"Done! {products_saved} new products and {prices_saved} price records saved to database")