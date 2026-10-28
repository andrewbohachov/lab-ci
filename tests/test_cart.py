from unittest.mock import Mock

import pytest

from shop.cart import Cart, RateProvider


# --- 1. Базові тести додавання та підрахунку ---
def test_cart_init_empty(empty_cart: Cart) -> None:
    assert empty_cart.items_count() == 0
    assert empty_cart.total() == 0.0


def test_add_new_item(empty_cart: Cart) -> None:
    empty_cart.add("notebook", price=150.0, qty=2)
    assert empty_cart.items_count() == 2
    assert empty_cart.total() == 300.0


def test_add_existing_item_increases_qty(cart_with_items: Cart) -> None:
    cart_with_items.add("apple", price=10.0, qty=3)
    assert cart_with_items.items_count() == 6  # було 3 + 3 = 6
    assert cart_with_items._items["apple"].qty == 5


def test_add_duplicate_item_keeps_original_price(cart_with_items: Cart) -> None:
    """Фіксація поведінки: якщо додати товар з існуючою назвою, але іншою ціною,

    поточна реалізація оновлює лише кількість, зберігаючи стару ціну.
    """
    cart_with_items.add("apple", price=999.0, qty=1)
    assert cart_with_items._items["apple"].price == 10.0
    assert cart_with_items._items["apple"].qty == 3


def test_remove_existing_item(cart_with_items: Cart) -> None:
    cart_with_items.remove("apple")
    assert cart_with_items.items_count() == 1
    assert "apple" not in cart_with_items._items


# --- 2. Перевірка винятків (pytest.raises) ---
def test_add_negative_price_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="price must be non-negative"):
        empty_cart.add("test", price=-10.0)


@pytest.mark.parametrize("invalid_qty", [0, -1, -10])
def test_add_invalid_qty_raises(empty_cart: Cart, invalid_qty: int) -> None:
    with pytest.raises(ValueError, match="qty must be positive"):
        empty_cart.add("test", price=10.0, qty=invalid_qty)


def test_remove_nonexistent_item_raises(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("nonexistent")


@pytest.mark.parametrize("invalid_discount", [-1.0, -0.01, 100.1, 150.0])
def test_total_invalid_discount_raises(cart_with_items: Cart, invalid_discount: float) -> None:
    with pytest.raises(ValueError, match=r"discount_percent must be in \[0, 100\]"):
        cart_with_items.total(discount_percent=invalid_discount)


# --- 3. Параметризований тест розрахунку знижок (граничні значення) ---
@pytest.mark.parametrize(
    ("discount", "expected_total"),
    [
        (0.0, 40.0),  # Граничне значення 0% (без знижки)
        (10.0, 36.0),  # Звичайна знижка 10%
        (50.0, 20.0),  # 50%
        (100.0, 0.0),  # Граничне значення 100% (безкоштовно)
    ],
)
def test_total_discounts_boundary(
    cart_with_items: Cart, discount: float, expected_total: float
) -> None:
    assert cart_with_items.total(discount_percent=discount) == pytest.approx(expected_total)


# --- 4. Тести з Mock (дублер RateProvider) ---
def test_total_in_currency_with_mock(cart_with_items: Cart) -> None:
    rates = Mock(spec=RateProvider)
    rates.get_rate.return_value = 40.0  # 1 USD = 40 UAH
    result = cart_with_items.total_in("USD", rates)

    assert result == 1.0  # 40.0 UAH / 40.0 = 1.0 USD
    rates.get_rate.assert_called_once_with("USD")


@pytest.mark.parametrize("bad_rate", [0.0, -5.0])
def test_total_in_invalid_rate_raises(cart_with_items: Cart, bad_rate: float) -> None:
    rates = Mock(spec=RateProvider)
    rates.get_rate.return_value = bad_rate
    with pytest.raises(ValueError, match="rate must be positive"):
        cart_with_items.total_in("EUR", rates)


# --- 5. TDD: тести для нового методу most_expensive() ---
def test_most_expensive_empty_cart(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None


def test_most_expensive_with_items(cart_with_items: Cart) -> None:
    # banana коштує 20.0, apple коштує 10.0
    item = cart_with_items.most_expensive()
    assert item is not None
    assert item.name == "banana"
    assert item.price == 20.0


def test_most_expensive_single_item(empty_cart: Cart) -> None:
    empty_cart.add("luxury", price=1000.0, qty=1)
    item = empty_cart.most_expensive()
    assert item is not None
    assert item.name == "luxury"
