from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ProductPage:
    NAME = (By.CSS_SELECTOR, "h1.product__name")
    PRICE = (By.CSS_SELECTOR, ".product__prices .product__price")
    QUANTITY = (By.ID, "quantity_wanted")
    INCREASE = (By.CSS_SELECTOR, ".product-quantity button.js-increment-button")
    DECREASE = (By.CSS_SELECTOR, ".product-quantity button.js-decrement-button")
    ADD_TO_CART = (By.CSS_SELECTOR, '[data-button-action="add-to-cart"]')

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver, 10, ignored_exceptions=(StaleElementReferenceException,)
        )

    def name(self):
        heading = self.wait.until(EC.visibility_of_element_located(self.NAME))
        return heading.text.strip()

    def selling_price(self):
        price = self.wait.until(EC.visibility_of_element_located(self.PRICE))
        return price.text.strip().removeprefix("Price:").strip()

    def quantity(self):
        field = self.wait.until(EC.visibility_of_element_located(self.QUANTITY))
        return int(field.get_property("value"))

    def increase_quantity(self):
        try:
            self.wait.until(
                lambda driver: self._click_quantity_button(driver, self.INCREASE),
                message="Could not click the + quantity button.",
            )
        except TimeoutException:
            self.driver.save_screenshot("tc04-click-failure.png")
            raise

    def try_decrease_quantity(self):
        self.wait.until(
            lambda driver: self._click_quantity_button(
                driver, self.DECREASE, allow_disabled=True
            ),
            message="Could not check or click the - quantity button.",
        )

    def _click_quantity_button(self, driver, locator, allow_disabled=False):
        button = EC.visibility_of_element_located(locator)(driver)
        if not button:
            return False

        if not button.is_enabled() or button.get_dom_attribute("aria-disabled") == "true":
            return allow_disabled

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
            button,
        )
        try:
            button.click()
        except ElementClickInterceptedException:
            return False

        return True

    def wait_for_quantity(self, expected):
        self.wait.until(
            lambda driver: (
                driver.find_element(*self.QUANTITY).get_property("value")
                == str(expected)
            ),
            message=f"Quantity did not change to {expected}.",
        )

    def add_to_cart_is_available(self):
        button = self.wait.until(EC.visibility_of_element_located(self.ADD_TO_CART))
        return button.is_enabled()