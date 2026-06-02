"""
tests/test_models.py
--------------------
Unit tests for the Product, PriceRecord, and PriceChange data models.

Run with:  python -m pytest tests/ -v
"""

import pytest
from datetime import datetime
from models.product import Product, PriceRecord, PriceChange


# ── Product tests ─────────────────────────────────────────────────────────────

class TestProduct:
    def test_basic_creation(self):
        p = Product(name="boAt Airdopes 141", url="https://example.com/p/1", source="Flipkart")
        assert p.name == "boAt Airdopes 141"
        assert p.source == "flipkart"   # should be lowercased
        assert p.id is None             # not saved to DB yet

    def test_whitespace_stripped(self):
        p = Product(name="  Some Product  ", url="https://example.com", source="  Amazon  ")
        assert p.name == "Some Product"
        assert p.source == "amazon"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="name cannot be empty"):
            Product(name="   ", url="https://example.com", source="flipkart")

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError, match="Invalid URL"):
            Product(name="Product", url="not-a-url", source="flipkart")

    def test_created_at_is_datetime(self):
        p = Product(name="Laptop", url="https://example.com/laptop", source="amazon")
        assert isinstance(p.created_at, datetime)

    def test_repr(self):
        p = Product(name="Keyboard", url="https://example.com/kb", source="amazon")
        assert "Keyboard" in repr(p)
        assert "amazon" in repr(p)


# ── PriceRecord tests ─────────────────────────────────────────────────────────

class TestPriceRecord:
    def test_basic_creation(self):
        r = PriceRecord(product_url="https://example.com/p/1", price=999.0)
        assert r.price == 999.0
        assert r.in_stock is True

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="negative"):
            PriceRecord(product_url="https://example.com/p/1", price=-50.0)

    def test_savings_calculated_correctly(self):
        r = PriceRecord(
            product_url="https://example.com/p/1",
            price=799.0,
            original_price=999.0,
        )
        assert r.savings == 200.0

    def test_savings_none_when_no_original(self):
        r = PriceRecord(product_url="https://example.com/p/1", price=799.0)
        assert r.savings is None

    def test_discount_pct_rounded(self):
        r = PriceRecord(product_url="https://x.com", price=100, discount_pct=33.33333)
        assert r.discount_pct == 33.33

    def test_repr_contains_price(self):
        r = PriceRecord(product_url="https://x.com", price=1499.0)
        assert "1499" in repr(r)


# ── PriceChange tests ─────────────────────────────────────────────────────────

class TestPriceChange:
    def _make_product(self):
        return Product(name="Phone", url="https://example.com/phone", source="amazon")

    def test_price_drop_detected(self):
        pc = PriceChange(product=self._make_product(), old_price=5000, new_price=3999)
        assert pc.is_drop is True
        assert pc.change_amount == -1001.0
        assert pc.change_pct < 0

    def test_price_rise_detected(self):
        pc = PriceChange(product=self._make_product(), old_price=3999, new_price=5000)
        assert pc.is_drop is False
        assert pc.change_amount == 1001.0
        assert pc.change_pct > 0

    def test_pct_calculation(self):
        pc = PriceChange(product=self._make_product(), old_price=1000, new_price=800)
        assert pc.change_pct == -20.0

    def test_zero_old_price_no_crash(self):
        pc = PriceChange(product=self._make_product(), old_price=0, new_price=100)
        assert pc.change_pct == 0.0

    def test_repr_shows_direction(self):
        pc = PriceChange(product=self._make_product(), old_price=500, new_price=400)
        assert "DROP" in repr(pc)
