import re
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.checkout_page import CheckoutPage
from pages.product_page import ProductPage


def money(text):
    if text.strip().casefold() == "free":
        return Decimal("0")

    match = re.search(r"\d[\d,]*(?:\.\d{1,2})?", text)
    if not match:
        raise ValueError(f"Could not read a price from {text!r}")

    return Decimal(match.group().replace(",", ""))


class OrderFlowPage(CheckoutPage):
    MODAL = (By.ID, "blockcart-modal")
    MODAL_PRODUCT = (By.CSS_SELECTOR, "#blockcart-modal .blockcart-modal__name")
    MODAL_QUANTITY = (By.CSS_SELECTOR, "#blockcart-modal .blockcart-modal__quantity")
    CONTINUE_SHOPPING = (
        By.CSS_SELECTOR,
        '#blockcart-modal .modal-footer button[data-bs-dismiss="modal"]',
    )
    CART_COUNT = (By.CSS_SELECTOR, "#_desktop_ps_shoppingcart .header-block__badge")
    SELECTED_VARIANTS = (By.CSS_SELECTOR, ".product__variants .product-variant")

    CART_LINES = (By.CSS_SELECTOR, ".js-cart-list .product-line")
    CART_NAME = (By.CSS_SELECTOR, ".product-line__content-left .product-line__title")
    CART_QUANTITY = (By.CSS_SELECTOR, "input.js-cart-line-product-quantity")
    CART_UNIT_PRICE = (By.CSS_SELECTOR, ".product-line__item-price")
    CART_LINE_TOTAL = (By.CSS_SELECTOR, ".product-line__price")
    CART_VARIANTS = (By.CSS_SELECTOR, ".product-line__item--info")
    CART_TOTAL_ROWS = (By.CSS_SELECTOR, ".js-cart-summary-totals .cart-summary__line")
    PRODUCTS_SUBTOTAL = (By.CSS_SELECTOR, "#cart-subtotal-products .cart-summary__value")
    SHIPPING_SUBTOTAL = (By.CSS_SELECTOR, "#cart-subtotal-shipping .cart-summary__value")
    TOTAL_LABEL = (By.CSS_SELECTOR, ".cart-summary__label")
    TOTAL_VALUE = (By.CSS_SELECTOR, ".cart-summary__value")

    COUNTRY = (By.CSS_SELECTOR, '#delivery-address select[name="id_country"]')
    CITY = (By.CSS_SELECTOR, '#delivery-address input[name="city"]')
    STATE = (By.CSS_SELECTOR, '#delivery-address select[name="id_state"]')
    POSTCODE = (By.CSS_SELECTOR, '#delivery-address input[name="postcode"]')
    ADDRESS_CONTINUE = (
        By.CSS_SELECTOR,
        '#checkout-addresses-step button[name="confirm-addresses"]',
    )
    DELIVERY_OPTION = (By.CSS_SELECTOR, '#js-delivery input[name^="delivery_option"]')
    DELIVERY_CONTINUE = (
        By.CSS_SELECTOR,
        '#js-delivery button[name="confirmDeliveryOption"]',
    )

    PAYMENT_STEP = (By.CSS_SELECTOR, "#checkout-payment-step.js-current-step")
    SUMMARY_TOGGLE = (
        By.CSS_SELECTOR,
        'button[data-bs-target="#cart-summary-product-list"]',
    )
    SUMMARY_LIST = (By.ID, "cart-summary-product-list")
    SUMMARY_LINES = (By.CSS_SELECTOR, "#cart-summary-product-list .cart-summary-product")
    SUMMARY_NAME = (By.CSS_SELECTOR, ".cart-summary-product__link")
    SUMMARY_QUANTITY = (By.CSS_SELECTOR, ".cart-summary-product__quantity .value")

    def _visible(self, locator):
        return self.wait.until(
            EC.visibility_of_element_located(locator),
            message=f"Could not see {locator[1]} on {self.driver.current_url}",
        )

    def selected_variants(self):
        variants = {}
        for field in self.driver.find_elements(*self.SELECTED_VARIANTS):
            name = field.find_element(By.TAG_NAME, "legend").text
            value = field.find_element(
                By.CSS_SELECTOR, ".product-variant__selected"
            ).get_property("textContent")
            variants[name.strip().casefold()] = value.strip().lstrip(":").strip()
        return variants

    def add_current_product(self):
        self._click(ProductPage.ADD_TO_CART, "Add to cart")
        self._visible(self.MODAL)

    def added_product(self):
        name = self._visible(self.MODAL_PRODUCT).text.strip()
        quantity_text = self._visible(self.MODAL_QUANTITY).text
        quantity = int(quantity_text.rsplit(":", 1)[-1].strip())
        return name.casefold(), quantity

    def continue_shopping(self):
        def popup_is_ready(driver):
            modal = driver.find_element(*self.MODAL)
            return driver.execute_script(
                """
                const modal = arguments[0];
                const dialog = modal.querySelector('.modal-dialog');
                if (!modal.classList.contains('show') || !dialog) {
                    return false;
                }
                return [modal, dialog].every(element =>
                    element.getAnimations().every(animation =>
                        animation.playState !== 'running' && !animation.pending
                    )
                );
                """,
                modal,
            )

        self.wait.until(
            popup_is_ready,
            message="The cart popup did not finish opening.",
        )
        self._click(self.CONTINUE_SHOPPING, "Continue shopping")
        self.wait.until(
            EC.invisibility_of_element_located(self.MODAL),
            message="The cart popup stayed open after clicking Continue shopping.",
        )

    def cart_count(self):
        return int(self._visible(self.CART_COUNT).text)

    def open_cart_from_popup(self):
        self._click(self.MODAL_CART_LINK, "Proceed to checkout in the cart popup")
        self._visible(self.CART_LINES)

    def cart_lines(self):
        lines = []
        rows = self.wait.until(EC.visibility_of_all_elements_located(self.CART_LINES))
        for row in rows:
            variants = {}
            for attribute in row.find_elements(*self.CART_VARIANTS):
                label, value = attribute.text.split(":", 1)
                variants[label.strip().casefold()] = value.strip()

            quantity = row.find_element(*self.CART_QUANTITY).get_property("value")
            lines.append({
                "name": row.find_element(*self.CART_NAME).text.strip().casefold(),
                "quantity": int(quantity),
                "unit_price": money(row.find_element(*self.CART_UNIT_PRICE).text),
                "line_total": money(row.find_element(*self.CART_LINE_TOTAL).text),
                "variants": variants,
            })
        return lines

    def products_subtotal(self):
        return money(self._visible(self.PRODUCTS_SUBTOTAL).text)

    def shipping_subtotal(self):
        return money(self._visible(self.SHIPPING_SUBTOTAL).text)

    def totals(self):
        totals = {}
        rows = self.wait.until(
            EC.visibility_of_all_elements_located(self.CART_TOTAL_ROWS)
        )
        for row in rows:
            label = row.find_element(*self.TOTAL_LABEL).text.strip().casefold()
            totals[label] = money(row.find_element(*self.TOTAL_VALUE).text)
        return totals

    def open_guest_checkout_from_cart(self):
        self._click(self.CART_CHECKOUT, "Proceed to checkout on the cart page")
        self._visible(self.EMAIL)

    def submit_shipping_address(self, country, street, city, state, postcode):
        country_field = self._visible(self.COUNTRY)
        if Select(country_field).first_selected_option.text.strip() != country:
            Select(country_field).select_by_visible_text(country)
            self.wait.until(EC.staleness_of(country_field))

        self._fill(self.SHIPPING_STREET, street)
        self._fill(self.CITY, city)
        self._fill(self.POSTCODE, postcode)
        if state:
            Select(self._visible(self.STATE)).select_by_visible_text(state)

        self._click(self.ADDRESS_CONTINUE, "Continue on the address form")
        self._visible(self.DELIVERY_OPTION)

    def continue_with_delivery(self):
        option = self._visible(self.DELIVERY_OPTION)
        selected = any(
            item.is_selected()
            for item in self.driver.find_elements(*self.DELIVERY_OPTION)
        )
        if not selected:
            self._click((By.ID, option.get_dom_attribute("id")), "a delivery option")

        self._click(self.DELIVERY_CONTINUE, "Continue on the delivery step")
        self._visible(self.PAYMENT_STEP)

    def order_summary_lines(self):
        if not self.driver.find_element(*self.SUMMARY_LIST).is_displayed():
            self._click(self.SUMMARY_TOGGLE, "Show cart details in the order summary")

        lines = self.wait.until(
            EC.visibility_of_all_elements_located(self.SUMMARY_LINES),
            message="Order summary product lines did not appear.",
        )
        return [
            (
                row.find_element(*self.SUMMARY_NAME).text.strip().casefold(),
                int(row.find_element(*self.SUMMARY_QUANTITY).text.strip().lstrip("x×")),
            )
            for row in lines
        ]