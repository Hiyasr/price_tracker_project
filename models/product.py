from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def current_time():
    return datetime.now(timezone.utc)


@dataclass
class Product:
    name: str
    url: str
    source: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=current_time)

    def __post_init__(self):
        self.name = self.name.strip()
        self.url = self.url.strip()
        self.source = self.source.lower().strip()

        if not self.name:
            raise ValueError("Product name cannot be empty.")
        if not self.url.startswith("http"):
            raise ValueError(f"Invalid URL: {self.url}")


@dataclass
class PriceRecord:
    product_url: str
    price: float
    original_price: Optional[float] = None
    discount_pct: Optional[float] = None
    in_stock: bool = True
    scraped_at: datetime = field(default_factory=current_time)
    id: Optional[int] = None

    def __post_init__(self):
        if self.price < 0:
            raise ValueError(f"Price cannot be negative: {self.price}")
        if self.discount_pct is not None:
            self.discount_pct = round(float(self.discount_pct), 2)

    @property
    def savings(self):
        if self.original_price:
            return round(self.original_price - self.price, 2)
        return None


@dataclass
class PriceChange:
    product: Product
    old_price: float
    new_price: float
    detected_at: datetime = field(default_factory=current_time)

    @property
    def change_amount(self):
        return round(self.new_price - self.old_price, 2)

    @property
    def change_pct(self):
        if self.old_price == 0:
            return 0.0
        return round((self.change_amount / self.old_price) * 100, 2)

    @property
    def is_drop(self):
        return self.change_amount < 0