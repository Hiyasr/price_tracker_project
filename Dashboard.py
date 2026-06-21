import os
import psycopg2
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Price Tracker Dashboard", layout="wide", page_icon="📊")


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


@st.cache_data(ttl=300)
def load_data():
    conn = get_connection()
    products_df = pd.read_sql("SELECT * FROM products", conn)
    history_df = pd.read_sql("SELECT * FROM price_history", conn)
    conn.close()

    history_df["price_clean"] = history_df["price"].apply(clean_price)
    history_df["mrp_clean"] = history_df["mrp"].apply(clean_price)
    history_df["scraped_at"] = pd.to_datetime(history_df["scraped_at"])

    return products_df, history_df


# Custom styling
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1c1f26; padding: 15px; border-radius: 10px; border: 1px solid #2a2e37; }
    h1, h2, h3 { color: #f0f0f0; }
</style>
""", unsafe_allow_html=True)

st.title("Price Tracker Dashboard")
st.caption("Real-time price tracking across Snapdeal categories")

products_df, history_df = load_data()

# Merge for latest data
merged = history_df.merge(products_df[["url", "name", "category"]], left_on="product_url", right_on="url", how="left")
latest = merged.sort_values("scraped_at").groupby("product_url").last().reset_index()
latest["discount_amount"] = latest["mrp_clean"] - latest["price_clean"]

# Top metrics row 
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Products Tracked", len(products_df))
with col2:
    st.metric("Total Price Records", len(history_df))
with col3:
    avg_price = latest["price_clean"].mean()
    st.metric("Average Price", f"₹{avg_price:,.0f}")
with col4:
    categories_count = products_df["category"].nunique()
    st.metric("Categories", categories_count)

st.divider()

# Charts row
col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Price by Category")
    avg_by_cat = latest.groupby("category")["price_clean"].mean().round(0).reset_index()
    fig = px.bar(avg_by_cat, x="category", y="price_clean", color="category",
                 labels={"price_clean": "Avg Price (₹)", "category": "Category"})
    fig.update_layout(showlegend=False, plot_bgcolor="#1c1f26", paper_bgcolor="#1c1f26", font_color="#f0f0f0")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Products per Category")
    cat_counts = products_df["category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    fig = px.pie(cat_counts, names="category", values="count", hole=0.4)
    fig.update_layout(plot_bgcolor="#1c1f26", paper_bgcolor="#1c1f26", font_color="#f0f0f0")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Top discounts table 
st.subheader("Top 10 Biggest Discounts")
top_discounts = latest.nlargest(10, "discount_amount")[["name", "category", "mrp_clean", "price_clean", "discount_amount"]]
top_discounts.columns = ["Product", "Category", "MRP (₹)", "Price (₹)", "You Save (₹)"]
st.dataframe(top_discounts, use_container_width=True, hide_index=True)

st.divider()

# Latest prices table 
st.subheader("Latest Prices")
search = st.text_input("Search products", placeholder="Type a product name...")

display_df = latest[["name", "category", "price_clean", "mrp_clean", "scraped_at"]].copy()
display_df.columns = ["Product", "Category", "Price (₹)", "MRP (₹)", "Last Updated"]

if search:
    display_df = display_df[display_df["Product"].str.contains(search, case=False, na=False)]

st.dataframe(display_df.sort_values("Last Updated", ascending=False), use_container_width=True, hide_index=True)

st.divider()

# ── Recent price changes ──────────────────────────────────────────────────────
st.subheader("Recent Price Changes")

changes = []
for url, group in merged.groupby("product_url"):
    group_sorted = group.sort_values("scraped_at")
    if len(group_sorted) >= 2:
        prev_price = group_sorted.iloc[-2]["price_clean"]
        curr_price = group_sorted.iloc[-1]["price_clean"]
        if prev_price and curr_price and prev_price != curr_price:
            changes.append({
                "Product": group_sorted.iloc[-1]["name"],
                "Category": group_sorted.iloc[-1]["category"],
                "Previous Price (₹)": prev_price,
                "Current Price (₹)": curr_price,
                "Change (₹)": round(curr_price - prev_price, 2),
                "Change (%)": round(((curr_price - prev_price) / prev_price) * 100, 2)
            })

if changes:
    changes_df = pd.DataFrame(changes).sort_values("Change (%)")
    st.dataframe(changes_df, use_container_width=True, hide_index=True)
else:
    st.info("No price changes detected yet. Run the scraper a few more times to build history.")

st.divider()
st.caption("Price Tracker & Market Insights Tool")