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


def clean_price(price_str):
    if not price_str:
        return None
    cleaned = price_str.replace("Rs.", "").replace("₹", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except:
        return None


def detect_price_changes():
    conn = get_connection()
    cursor = conn.cursor()

    # Get all products
    cursor.execute("SELECT id, name, url FROM products")
    products = cursor.fetchall()

    increased = []
    decreased = []
    unchanged = []
    no_history = []

    for product_id, name, url in products:
        # Get last 2 price records for this product
        cursor.execute("""
            SELECT price, scraped_at
            FROM price_history
            WHERE product_url = %s
            ORDER BY scraped_at DESC
            LIMIT 2
        """, (url,))

        records = cursor.fetchall()

        if len(records) < 2:
            no_history.append(name)
            continue

        latest_price = clean_price(records[0][0])
        previous_price = clean_price(records[1][0])

        if latest_price is None or previous_price is None:
            continue

        change_amount = round(latest_price - previous_price, 2)
        change_pct = round((change_amount / previous_price) * 100, 2) if previous_price != 0 else 0

        result = {
            "name": name,
            "previous_price": previous_price,
            "latest_price": latest_price,
            "change_amount": change_amount,
            "change_pct": change_pct,
        }

        if change_amount > 0:
            increased.append(result)
        elif change_amount < 0:
            decreased.append(result)
        else:
            unchanged.append(result)

    cursor.close()
    conn.close()

    return {
        "increased": increased,
        "decreased": decreased,
        "unchanged": unchanged,
        "no_history": no_history
    }


def print_report(changes):
    print("\n" + "="*60)
    print("PRICE CHANGE REPORT")
    print("="*60)

    print(f"\n📈 INCREASED ({len(changes['increased'])} products)")
    for p in changes["increased"][:5]:
        print(f"  {p['name'][:50]}")
        print(f"    ₹{p['previous_price']} → ₹{p['latest_price']} (+{p['change_pct']}%)")

    print(f"\n📉 DECREASED ({len(changes['decreased'])} products)")
    for p in changes["decreased"][:5]:
        print(f"  {p['name'][:50]}")
        print(f"    ₹{p['previous_price']} → ₹{p['latest_price']} ({p['change_pct']}%)")

    print(f"\n➡️  UNCHANGED ({len(changes['unchanged'])} products)")
    print(f"\n⚠️  NOT ENOUGH HISTORY ({len(changes['no_history'])} products)")

    print("\n" + "="*60)
    print(f"SUMMARY: {len(changes['increased'])} increased | {len(changes['decreased'])} decreased | {len(changes['unchanged'])} unchanged")
    print("="*60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    changes = detect_price_changes()
    print_report(changes)