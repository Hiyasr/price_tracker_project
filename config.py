"""
config.py
---------
Central configuration for the Price Tracker application.

All settings — database credentials, scraping delays, file paths — live here.
Never hardcode these values inside scrapers or other modules.

To use:
    from config import config
    print(config.DB_NAME)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

# ── Project root (the folder this file lives in) ─────────────────────────────
BASE_DIR = Path(__file__).parent


@dataclass
class Config:
    # ── Database ──────────────────────────────────────────────────────────────
    # In Phase 3 you'll fill these in. For now they read from environment
    # variables so we never commit real credentials to Git.
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "price_tracker")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # ── Scraping ──────────────────────────────────────────────────────────────
    # Delay between HTTP requests (seconds). Be polite to servers!
    REQUEST_DELAY: float = 2.0
    # How many times to retry a failed request before giving up
    MAX_RETRIES: int = 3
    # Timeout for a single HTTP request (seconds)
    REQUEST_TIMEOUT: int = 15
    # Browser-like User-Agent header so sites don't block us immediately
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # ── File paths ────────────────────────────────────────────────────────────
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_DIR: Path = BASE_DIR / "logs"
    REPORTS_DIR: Path = BASE_DIR / "data" / "reports"

    # ── Websites to scrape ────────────────────────────────────────────────────
    # Each entry: { "name": str, "base_url": str, "enabled": bool }
    # Phase 2 will add the actual scraping logic for each site.
    SOURCES: list = field(default_factory=lambda: [
        {
            "name": "books_to_scrape",
            "base_url": "https://books.toscrape.com",
            "enabled": True,
            "notes": "Practice site — legal to scrape, no login needed",
        },
        {
            "name": "quotes_to_scrape",
            "base_url": "https://quotes.toscrape.com",
            "enabled": False,
            "notes": "Backup practice site",
        },
        # When you're ready for real sites, add them here and build
        # a dedicated scraper module in scrapers/
    ])

    def __post_init__(self):
        """Create necessary directories if they don't exist yet."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def db_url(self) -> str:
        """SQLAlchemy-compatible database URL (useful in Phase 3)."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Single shared instance — import this everywhere
config = Config()
