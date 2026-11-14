from decimal import Decimal

from pages.order_flow_page import OrderFlowPage, money


ONE_CENT = Decimal("0.01")


def test_tc15_two_products_reach_guest_order_summary(
    storefront_driver, search_page, shirt_page
):
    order = OrderFlowPage(storefront_driver)
    shirt = "Hummingbird printed t-shirt"
    mug = "Mug The Adventure Begins"

    search_page.search(shirt)
    search_page.open_product_from_results(shirt)
    assert shirt_page.name().casefold() == shirt.casefold()

    shirt_price = money(shirt_page.selling_price())
    shirt_variants = order.selected_variants()
    assert shirt_variants, "Expected a selected T-shirt variant."
    assert shirt_page.quantity() == 1

    shirt_page.increase_quantity()
    shirt_page.wait_for_quantity(2)
    assert shirt_page.quantity() == 2

    order.add_current_product()
    assert order.added_product() == (shirt.casefold(), 2)

    order.continue_shopping()
    assert order.cart_count() == 2

    search_page.search(mug)
    search_page.open_product_from_results(mug)
    assert shirt_page.name().casefold() == mug.casefold()

    mug_price = money(shirt_page.selling_price())
    assert shirt_page.quantity() == 1

    order.add_current_product()
    assert order.added_product() == (mug.casefold(), 1)
    order.open_cart_from_popup()

    lines = order.cart_lines()
    assert len(lines) == 2

    by_name = {line["name"]: line for line in lines}
    assert set(by_name) == {shirt.casefold(), mug.casefold()}

    shirt_line = by_name[shirt.casefold()]
    mug_line = by_name[mug.casefold()]

    assert shirt_line["quantity"] == 2
    assert mug_line["quantity"] == 1
    assert order.cart_count() == 3
    assert shirt_line["variants"] == shirt_variants
    assert shirt_line["unit_price"] == shirt_price
    assert mug_line["unit_price"] == mug_price

    expected_shirt_total = 2 * shirt_price
    actual_shirt_total = shirt_line["line_total"]
    assert abs(actual_shirt_total - expected_shirt_total) <= ONE_CENT, (
        f"T-shirt line total was {actual_shirt_total}. "
        f"Expected {expected_shirt_total} within one cent."
    )
    assert mug_line["line_total"] == mug_price

    line_totals_sum = actual_shirt_total + mug_line["line_total"]
    subtotal = order.products_subtotal()
    assert abs(subtotal - line_totals_sum) <= ONE_CENT, (
        f"Cart subtotal was {subtotal}. "
        f"Displayed line totals add up to {line_totals_sum}."
    )

    cart_totals = order.totals()
    displayed_totals = [
        amount for label, amount in cart_totals.items()
        if label.startswith("total")
    ]
    assert displayed_totals, "The cart did not show a total."
    assert displayed_totals[0] == subtotal + order.shipping_subtotal()

    order.open_guest_checkout_from_cart()
    order.enter_guest_details("Alex", "Morgan", "alex.morgan.qa@example.com")
    order.submit_guest_details()
    assert order.shipping_address_is_visible()

    order.submit_shipping_address(
        country="United States",
        street="123 Test Avenue",
        city="San Francisco",
        state="California",
        postcode="94105",
    )
    order.continue_with_delivery()

    assert sorted(order.order_summary_lines()) == sorted([
        (shirt.casefold(), 2),
        (mug.casefold(), 1),
    ])
    checkout_totals = [
        amount for label, amount in order.totals().items()
        if label.startswith("total")
    ]
    assert checkout_totals, "The order summary did not show a total."
    assert checkout_totals[-1] > Decimal("0")