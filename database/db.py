import os
import psycopg2
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "price_tracker"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )


def save_products(products: list):
    conn = get_connection()
    cursor = conn.cursor()
    products_saved = 0
    prices_saved = 0

    for p in products:
        try:
            # Insert product - skip if URL already exists
            cursor.execute("""
                INSERT INTO products (name, url, source, category)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
            """, (p["name"], p["url"], p["source"], p.get("category")))

            products_saved += cursor.rowcount

            # Always insert a new price record
            cursor.execute("""
                INSERT INTO price_history (product_url, price, mrp, discount, rating, availability)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                p["url"],
                p.get("price"),
                p.get("mrp"),
                p.get("discount"),
                p.get("rating"),
                p.get("availability")
            ))

            prices_saved += 1

        except Exception as e:
            logger.warning(f"Failed to save product: {e}")
            conn.rollback()
            continue

    conn.commit()
    cursor.close()
    conn.close()

    logger.info(f"Saved {products_saved} new products and {prices_saved} price records")
    return products_saved, prices_saved