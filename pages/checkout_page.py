from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.product_page import ProductPage


class CheckoutPage:
    MODAL_CART_LINK = (By.CSS_SELECTOR, "#blockcart-modal .modal-footer a.btn-primary")
    CART_CHECKOUT = (By.CSS_SELECTOR, ".js-cart-detailed-actions a.btn-primary")
    FIRST_NAME = (By.CSS_SELECTOR, '#checkout-guest-form input[name="firstname"]')
    LAST_NAME = (By.CSS_SELECTOR, '#checkout-guest-form input[name="lastname"]')
    EMAIL = (By.CSS_SELECTOR, '#checkout-guest-form input[name="email"]')
    CONSENT_BOXES = (By.CSS_SELECTOR, '#checkout-guest-form input[type="checkbox"]')
    GUEST_CONTINUE = (By.CSS_SELECTOR, '#checkout-guest-form button[name="continue"]')
    SHIPPING_STREET = (By.CSS_SELECTOR, '#delivery-address input[name="address1"]')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver, 10, ignored_exceptions=(StaleElementReferenceException,)
        )

    def _click(self, locator, description):
        def click_when_ready(driver):
            element = EC.element_to_be_clickable(locator)(driver)
            if not element:
                return False

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
                element,
            )
            try:
                element.click()
            except ElementClickInterceptedException:
                return False
            return True

        try:
            self.wait.until(
                click_when_ready,
                message=f"TC-14: Could not click {description}.",
            )
        except TimeoutException:
            self.driver.save_screenshot("tc14-click-failure.png")
            raise

    def _fill(self, locator, value):
        field = self.wait.until(EC.visibility_of_element_located(locator))
        field.clear()
        field.send_keys(value)

    def open_guest_checkout_with_current_product(self):
        self._click(ProductPage.ADD_TO_CART, "Add to cart")
        self._click(self.MODAL_CART_LINK, "Proceed to checkout in the cart popup")
        self._click(self.CART_CHECKOUT, "Proceed to checkout on the cart page")
        self.wait.until(EC.visibility_of_element_located(self.EMAIL))

    def enter_guest_details(self, first_name, last_name, email):
        self._fill(self.FIRST_NAME, first_name)
        self._fill(self.LAST_NAME, last_name)
        self.set_email(email)

    def set_email(self, email):
        self._fill(self.EMAIL, email)

    def submit_guest_details(self):
        for checkbox in self.driver.find_elements(*self.CONSENT_BOXES):
            name = checkbox.get_dom_attribute("name")
            required = checkbox.get_property("required") or name in {
                "customer_privacy",
                "psgdpr",
            }
            if required and checkbox.is_displayed() and not checkbox.is_selected():
                locator = (
                    By.CSS_SELECTOR,
                    f'#checkout-guest-form input[type="checkbox"][name="{name}"]',
                )
                self._click(locator, f"the {name} consent checkbox")
                self.wait.until(EC.element_located_to_be_selected(locator))

        self._click(self.GUEST_CONTINUE, "Continue on the guest details form")

    def email_validation_message(self):
        def read_message(driver):
            field = EC.visibility_of_element_located(self.EMAIL)(driver)
            return field.get_property("validationMessage") if field else False

        return self.wait.until(
            read_message,
            message="The guest email field did not report a validation error.",
        )

    def guest_form_is_visible(self):
        return any(
            field.is_displayed() for field in self.driver.find_elements(*self.EMAIL)
        )

    def shipping_address_is_visible(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.SHIPPING_STREET),
            message="The shipping address form did not open.",
        ).is_displayed()