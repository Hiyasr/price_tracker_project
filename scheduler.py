import schedule
import time
import logging
from datetime import datetime
from utils.logger import get_logger
from scrapers.snapdeal_scraper import SnapdealScraper
from database.db import save_products

logger = get_logger(__name__)

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


def run_daily_scrape():
    logger.info("===== Daily scrape started =====")
    start_time = datetime.now()

    all_products = []
    scraper = SnapdealScraper(delay=2.0)

    for category in CATEGORIES:
        try:
            logger.info(f"Scraping category: {category['name']}")
            products = scraper.scrape(category["url"])

            if not products:
                logger.warning(f"No products found for {category['name']}")
                continue

            for p in products:
                p["category"] = category["name"]
            all_products.extend(products)
            logger.info(f"Collected {len(products)} products from {category['name']}")

        except Exception as e:
            logger.error(f"Failed to scrape {category['name']}: {e}")
            continue

    logger.info(f"Total products collected: {len(all_products)}")

    if not all_products:
        logger.error("No products collected in this run. Skipping database save.")
        return

    try:
        products_saved, prices_saved = save_products(all_products)
        logger.info(f"Database updated: {products_saved} new products, {prices_saved} price records")
    except Exception as e:
        logger.error(f"Database save failed: {e}")
        return

    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"===== Daily scrape completed in {duration:.1f} seconds =====")


def start_scheduler():
    # Run once immediately, then every day at 9 AM
    schedule.every().day.at("09:00").do(run_daily_scrape)
    logger.info("Scheduler started. Waiting for scheduled time (09:00 daily)...")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "now":
        # Run immediately for testing
        run_daily_scrape()
    else:
        start_scheduler()