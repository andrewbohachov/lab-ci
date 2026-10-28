import pytest

from shop.cart import Cart


@pytest.fixture
def empty_cart() -> Cart:
    """Порожній кошик для тестів."""
    return Cart()


@pytest.fixture
def cart_with_items() -> Cart:
    """Кошик із двома товарами:

    - apple: ціна 10.0, кількість 2 (сума 20.0)
    - banana: ціна 20.0, кількість 1 (сума 20.0)
    Загальна вартість: 40.0 грн, кількість товарів: 3 шт.
    """
    cart = Cart()
    cart.add("apple", price=10.0, qty=2)
    cart.add("banana", price=20.0, qty=1)
    return cart
