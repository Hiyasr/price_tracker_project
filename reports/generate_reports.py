import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
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
    try:
        return float(price_str.replace("Rs.", "").replace("₹", "").replace(",", "").strip())
    except:
        return None


def load_data():
    conn = get_connection()

    products_df = pd.read_sql("SELECT * FROM products", conn)
    history_df = pd.read_sql("SELECT * FROM price_history", conn)

    conn.close()

    history_df["price_clean"] = history_df["price"].apply(clean_price)
    history_df["mrp_clean"] = history_df["mrp"].apply(clean_price)

    return products_df, history_df


def generate_reports():
    print("\nLoading data from database...")
    products_df, history_df = load_data()

    # Merge products with price history
    merged = history_df.merge(products_df[["url", "name", "category"]], left_on="product_url", right_on="url", how="left")

    # ── 1. Average price per category ─────────────────────────────────────────
    avg_by_category = merged.groupby("category")["price_clean"].mean().round(2).reset_index()
    avg_by_category.columns = ["category", "avg_price"]

    # ── 2. Most expensive products ────────────────────────────────────────────
    latest_prices = merged.sort_values("scraped_at").groupby("product_url").last().reset_index()
    top_expensive = latest_prices.nlargest(10, "price_clean")[["name", "category", "price_clean"]]
    top_expensive.columns = ["name", "category", "price"]

    # ── 3. Biggest discounts ──────────────────────────────────────────────────
    latest_prices["discount_clean"] = latest_prices["mrp_clean"] - latest_prices["price_clean"]
    top_discounts = latest_prices.nlargest(10, "discount_clean")[["name", "category", "mrp_clean", "price_clean", "discount_clean"]]
    top_discounts.columns = ["name", "category", "mrp", "price", "savings"]

    # ── 4. Most frequently scraped products ───────────────────────────────────
    scrape_count = merged.groupby("name")["scraped_at"].count().reset_index()
    scrape_count.columns = ["name", "scrape_count"]
    most_tracked = scrape_count.nlargest(10, "scrape_count")

    # ── Print summaries ───────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("PRICE TRACKER - ANALYSIS REPORT")
    print("="*60)

    print("\n📊 AVERAGE PRICE BY CATEGORY")
    print(avg_by_category.to_string(index=False))

    print("\n💰 TOP 10 MOST EXPENSIVE PRODUCTS")
    print(top_expensive.to_string(index=False))

    print("\n🏷️  TOP 10 BIGGEST DISCOUNTS")
    print(top_discounts.to_string(index=False))

    print("\n🔄 MOST FREQUENTLY TRACKED PRODUCTS")
    print(most_tracked.to_string(index=False))

    # ── Export reports ────────────────────────────────────────────────────────
    os.makedirs("data/reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # CSV
    csv_path = f"data/reports/report_{timestamp}.csv"
    latest_prices[["name", "category", "price_clean", "mrp_clean", "discount_clean"]].to_csv(csv_path, index=False)
    print(f"\n✅ CSV saved to {csv_path}")

    # Excel
    excel_path = f"data/reports/report_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        avg_by_category.to_excel(writer, sheet_name="Avg Price by Category", index=False)
        top_expensive.to_excel(writer, sheet_name="Most Expensive", index=False)
        top_discounts.to_excel(writer, sheet_name="Biggest Discounts", index=False)
        most_tracked.to_excel(writer, sheet_name="Most Tracked", index=False)

    print(f"✅ Excel saved to {excel_path}")
    print("\nDone!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_reports()