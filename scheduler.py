import schedule
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger
from scrapers.snapdeal_scraper import SnapdealScraper
from database.db import save_products

logger = get_logger(__name__)

RUN_HISTORY_FILE = Path(__file__).parent / "logs" / "run_history.json"

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


def save_run_summary(summary: dict):
    """Append this run's summary to the run history JSON file."""
    history = []
    if RUN_HISTORY_FILE.exists():
        try:
            with open(RUN_HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append(summary)

    with open(RUN_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def run_daily_scrape():
    logger.info("===== Daily scrape started =====")
    start_time = datetime.now()

    summary = {
        "started_at": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": None,
        "duration_seconds": None,
        "categories": {},
        "total_products_collected": 0,
        "new_products_saved": 0,
        "price_records_saved": 0,
        "errors": []
    }

    all_products = []
    scraper = SnapdealScraper(delay=2.0)

    for category in CATEGORIES:
        try:
            logger.info(f"Scraping category: {category['name']}")
            products = scraper.scrape(category["url"])

            if not products:
                logger.warning(f"No products found for {category['name']}")
                summary["categories"][category["name"]] = 0
                summary["errors"].append(f"{category['name']}: no products found")
                continue

            for p in products:
                p["category"] = category["name"]
            all_products.extend(products)
            summary["categories"][category["name"]] = len(products)
            logger.info(f"Collected {len(products)} products from {category['name']}")

        except Exception as e:
            logger.error(f"Failed to scrape {category['name']}: {e}")
            summary["categories"][category["name"]] = 0
            summary["errors"].append(f"{category['name']}: {str(e)}")
            continue

    summary["total_products_collected"] = len(all_products)
    logger.info(f"Total products collected: {len(all_products)}")

    if not all_products:
        logger.error("No products collected in this run. Skipping database save.")
        summary["errors"].append("No products collected - database save skipped")
    else:
        try:
            products_saved, prices_saved = save_products(all_products)
            summary["new_products_saved"] = products_saved
            summary["price_records_saved"] = prices_saved
            logger.info(f"Database updated: {products_saved} new products, {prices_saved} price records")
        except Exception as e:
            logger.error(f"Database save failed: {e}")
            summary["errors"].append(f"Database save failed: {str(e)}")

    finish_time = datetime.now()
    duration = (finish_time - start_time).total_seconds()
    summary["finished_at"] = finish_time.strftime("%Y-%m-%d %H:%M:%S")
    summary["duration_seconds"] = round(duration, 1)

    save_run_summary(summary)

    logger.info(f"===== Daily scrape completed in {duration:.1f} seconds =====")
    logger.info(f"Run summary saved to {RUN_HISTORY_FILE}")

    return summary


def start_scheduler():
    schedule.every().day.at("09:00").do(run_daily_scrape)
    logger.info("Scheduler started. Waiting for scheduled time (09:00 daily)...")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "now":
        run_daily_scrape()
    else:
        start_scheduler()