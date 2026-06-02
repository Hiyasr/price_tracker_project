"""
models/product.py
-----------------
Core data models for the Price Tracker application.

These classes define the shape of our data. Think of them as blueprints —
every product and every price record in the system will follow these structures.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


@dataclass
class Product:
    """
    Represents a single product we are tracking.

    A product is identified by its URL — the same item on the same website
    is always the same product, regardless of price changes.

    Attributes:
        name        : Human-readable product title (e.g. "boAt Airdopes 141")
        url         : Canonical product page URL — used as unique identifier
        source      : Website this product was scraped from (e.g. "flipkart")
        category    : Optional category tag (e.g. "electronics", "fashion")
        image_url   : Optional link to the product thumbnail
        id          : Auto-assigned database ID (None until saved to DB)
        created_at  : Timestamp when we first discovered this product
    """

    name: str
    url: str
    source: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self):
        """Validate and clean data right after the object is created."""
        self.name = self.name.strip()
        self.url = self.url.strip()
        self.source = self.source.lower().strip()

        if not self.name:
            raise ValueError("Product name cannot be empty.")
        if not self.url.startswith("http"):
            raise ValueError(f"Invalid URL: {self.url}")

    def __repr__(self):
        return f"Product(name={self.name!r}, source={self.source!r}, url={self.url!r})"


@dataclass
class PriceRecord:
    """
    Represents the price of a product at a specific point in time.

    Every time we scrape a product we create a new PriceRecord. This is what
    lets us track how prices change — we never overwrite old prices.

    Attributes:
        product_url     : Foreign key back to the Product this price belongs to
        price           : Price in INR (₹), stored as a float
        original_price  : Listed "original" / MRP price if a discount is shown
        discount_pct    : Discount percentage as shown on the site (0–100)
        in_stock        : Whether the product was available at scrape time
        scraped_at      : Exact UTC timestamp of this scrape
        id              : Auto-assigned database ID (None until saved to DB)
    """

    product_url: str
    price: float
    original_price: Optional[float] = None
    discount_pct: Optional[float] = None
    in_stock: bool = True
    scraped_at: datetime = field(default_factory=_utcnow)
    id: Optional[int] = None

    def __post_init__(self):
        if self.price < 0:
            raise ValueError(f"Price cannot be negative: {self.price}")
        if self.original_price is not None and self.original_price < self.price:
            # Some sites show weird data; log but don't crash
            pass
        if self.discount_pct is not None:
            self.discount_pct = round(float(self.discount_pct), 2)

    @property
    def savings(self) -> Optional[float]:
        """Absolute money saved if original price is known."""
        if self.original_price:
            return round(self.original_price - self.price, 2)
        return None

    def __repr__(self):
        return (
            f"PriceRecord(price=₹{self.price}, "
            f"in_stock={self.in_stock}, "
            f"scraped_at={self.scraped_at.strftime('%Y-%m-%d %H:%M')})"
        )


@dataclass
class PriceChange:
    """
    Represents a detected price change between two PriceRecords.

    Created by the price-change detection logic (Phase 4). Useful for
    generating alerts and reports without re-querying the database.

    Attributes:
        product         : The product that changed in price
        old_price       : Price before the change
        new_price       : Price after the change
        change_amount   : Absolute difference (new - old); negative = price drop
        change_pct      : Percentage change; negative = price drop
        detected_at     : When this change was detected
    """

    product: Product
    old_price: float
    new_price: float
    detected_at: datetime = field(default_factory=_utcnow)

    @property
    def change_amount(self) -> float:
        return round(self.new_price - self.old_price, 2)

    @property
    def change_pct(self) -> float:
        if self.old_price == 0:
            return 0.0
        return round((self.change_amount / self.old_price) * 100, 2)

    @property
    def is_drop(self) -> bool:
        return self.change_amount < 0

    def __repr__(self):
        direction = "↓ DROP" if self.is_drop else "↑ RISE"
        return (
            f"PriceChange({direction} ₹{self.old_price} → ₹{self.new_price} "
            f"({self.change_pct:+.1f}%) for {self.product.name!r})"
        )
