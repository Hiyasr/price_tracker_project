# 🏷️ Price Tracker & Market Insights Tool

A Python application that tracks product prices across e-commerce websites, stores historical data, and generates reports on pricing trends.

---

## 📁 Project Structure

```
price_tracker/
├── scrapers/           # One module per website (Phase 2)
│   └── __init__.py
├── models/             # Data models: Product, PriceRecord, PriceChange
│   ├── __init__.py
│   └── product.py
├── database/           # PostgreSQL connection & queries (Phase 3)
│   └── __init__.py
├── reports/            # CSV / Excel / console report generators (Phase 5)
│   └── __init__.py
├── utils/              # Shared helpers: logger, HTTP client, etc.
│   ├── __init__.py
│   └── logger.py
├── tests/              # Unit tests (run with pytest)
│   ├── __init__.py
│   └── test_models.py
├── logs/               # Auto-generated log files (gitignored)
├── data/               # Scraped data & reports (gitignored)
├── config.py           # All application settings in one place
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd price_tracker
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Run the tests
```bash
python -m pytest tests/ -v
```

---

## 🌐 Target Websites

| Site | URL | Why |
|------|-----|-----|
| Books to Scrape | https://books.toscrape.com | Legal practice site, perfect for Phase 2 |
| Quotes to Scrape | https://quotes.toscrape.com | Backup practice site |
| *(Add real site here)* | — | Phase 2 onwards |

> **Note on real sites:** Before scraping any website, always check its `robots.txt` (e.g. `https://example.com/robots.txt`) and Terms of Service. Add a delay between requests (`config.REQUEST_DELAY`) and never hammer a server.

---

## 📦 Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ Done | Project setup, data models, structure |
| 2 | 🔜 Next | Build scrapers, collect 50+ products per site |
| 3 | — | PostgreSQL integration, store price history |
| 4 | — | Price change detection & alerts |
| 5 | — | Reports with Pandas (CSV, Excel) |
| 6 | — | Automated daily scheduling + logging |
| 7 | — | Streamlit dashboard (optional) |

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing
```

---

## 🔑 Key Design Decisions

- **Dataclasses** are used for models instead of plain dicts — they give us type hints, validation, and a clean `repr()` for free.
- **Config is centralised** in `config.py` — no magic strings scattered around the codebase.
- **Secrets live in `.env`** — never hardcoded, never committed to Git.
- **Logging is structured** — every module gets its own named logger, all output goes to both console and a rotating file.

---

## 📝 License

Built as an internship project. Not for commercial use.
