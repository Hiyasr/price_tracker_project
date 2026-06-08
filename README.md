# Price Tracker & Market Insights Tool

A Python app that tracks product prices from e-commerce websites and shows how prices change over time.

---

## Project Structure

```
price_tracker/
├── scrapers/        # Website scrapers (Phase 2)
├── models/          # Product, PriceRecord, PriceChange classes
├── database/        # PostgreSQL setup (Phase 3)
├── reports/         # Report generation (Phase 5)
├── utils/           # Logger and helper functions
├── tests/           # Unit tests
├── logs/            # Auto-generated log files
├── data/            # Scraped data and reports
├── config.py        # All app settings
└── requirements.txt
test_run_ss # output screenshots
```

---

## Setup

**1. Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**
```bash
cp .env.example .env
# open .env and fill in your database credentials
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Target Websites

| Site | URL |
|------|-----|
| Books to Scrape | https://books.toscrape.com |
| Quotes to Scrape | https://quotes.toscrape.com |

---

## Progress

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ Done | Project setup, data models, structure |
| 2 | 🔜 Next | Build scrapers, collect products |
| 3 | ⏳ | Database integration |
| 4 | ⏳ | Price change detection |
| 5 | ⏳ | Reports and analysis |
| 6 | ⏳ | Automation and scheduling |
| 7 | ⏳ | Streamlit dashboard (optional) |
