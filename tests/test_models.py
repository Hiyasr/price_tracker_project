import pytest
from models.product import Product, PriceRecord, PriceChange


class TestProduct:
    def test_basic_creation(self):
        p = Product(name="A Light in the Attic", url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html", source="books_to_scrape")
        assert p.name == "A Light in the Attic"
        assert p.source == "books_to_scrape"
        assert p.id is None

    def test_whitespace_stripped(self):
        p = Product(name="  Some Book  ", url="https://books.toscrape.com", source="  Books  ")
        assert p.name == "Some Book"
        assert p.source == "books"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            Product(name="   ", url="https://books.toscrape.com", source="books_to_scrape")

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError):
            Product(name="Some Book", url="not-a-url", source="books_to_scrape")


class TestPriceRecord:
    def test_basic_creation(self):
        r = PriceRecord(product_url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html", price=51.77)
        assert r.price == 51.77
        assert r.in_stock is True

    def test_negative_price_raises(self):
        with pytest.raises(ValueError):
            PriceRecord(product_url="https://books.toscrape.com", price=-10.0)

    def test_savings_calculated(self):
        r = PriceRecord(product_url="https://books.toscrape.com", price=40.0, original_price=50.0)
        assert r.savings == 10.0

    def test_savings_none_when_no_original(self):
        r = PriceRecord(product_url="https://books.toscrape.com", price=40.0)
        assert r.savings is None


class TestPriceChange:
    def _product(self):
        return Product(name="A Light in the Attic", url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html", source="books_to_scrape")

    def test_price_drop(self):
        pc = PriceChange(product=self._product(), old_price=51.77, new_price=40.00)
        assert pc.is_drop is True
        assert pc.change_amount == -11.77

    def test_price_rise(self):
        pc = PriceChange(product=self._product(), old_price=40.00, new_price=51.77)
        assert pc.is_drop is False

    def test_percentage_calculation(self):
        pc = PriceChange(product=self._product(), old_price=100.0, new_price=80.0)
        assert pc.change_pct == -20.0