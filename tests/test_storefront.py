from pages.catalog_page import CatalogPage
from pages.checkout_page import CheckoutPage


def test_tc04_increase_quantity(shirt_page):
    assert shirt_page.quantity() == 1

    shirt_page.increase_quantity()
    shirt_page.wait_for_quantity(2)

    assert shirt_page.quantity() == 2
    assert shirt_page.add_to_cart_is_available()


def test_tc05_quantity_cannot_go_below_one(shirt_page):
    assert shirt_page.quantity() == 1

    shirt_page.try_decrease_quantity()

    assert shirt_page.quantity() == 1


def test_tc02_search_returns_no_products(search_page):
    search_term = "qa-no-match-73951"

    search_page.search(search_term)
    heading = search_page.results_heading()

    assert "no search results" in heading.casefold()
    assert search_term in heading.casefold()
    assert search_page.product_count() == 0


def test_tc03_open_shirt_from_search_results(search_page, shirt_page):
    product_name = "Hummingbird printed t-shirt"

    search_page.search(product_name)
    result_name, result_price = search_page.open_product_from_results(product_name)

    assert result_name.casefold() == product_name.casefold()
    assert shirt_page.name().casefold() == result_name.casefold()
    assert " ".join(shirt_page.selling_price().split()) == " ".join(result_price.split())
    assert shirt_page.quantity() == 1
    assert shirt_page.add_to_cart_is_available()


def test_tc01_category_prices_sort_low_to_high(storefront_driver):
    catalog = CatalogPage(storefront_driver)

    catalog.open_accessories()
    assert catalog.category_name().casefold() == "accessories"

    catalog.sort_by_lowest_price()

    prices = []
    while True:
        assert catalog.category_name().casefold() == "accessories"
        assert "price, low to high" in catalog.selected_sort().casefold()
        prices.extend(catalog.prices_on_current_page())

        if not catalog.go_to_next_page():
            break

    assert len(set(prices)) >= 3, "Accessories needs at least three distinct prices."
    assert prices == sorted(prices), f"Prices are out of order: {prices}"

def test_tc14_invalid_guest_email_is_rejected(storefront_driver):
    checkout = CheckoutPage(storefront_driver)
    checkout.open_guest_checkout_with_current_product()

    checkout.enter_guest_details("Alex", "Morgan", "alex.morgan.qa.example.com")
    checkout.submit_guest_details()

    assert checkout.email_validation_message()
    assert checkout.guest_form_is_visible()

    checkout.set_email("alex.morgan.qa@example.com")
    checkout.submit_guest_details()

    assert checkout.shipping_address_is_visible()
