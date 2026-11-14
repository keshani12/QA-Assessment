import re
from decimal import Decimal

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CatalogPage:
    ACCESSORIES = (
        By.XPATH,
        "//header//a[translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'accessories']",
    )
    CATEGORY_HEADING = (By.ID, "js-product-list-header")
    SORT_BUTTON = (By.ID, "sort_dropdown_button")
    PRICE_LOW_TO_HIGH = (
        By.CSS_SELECTOR,
        '.js-search-link[href*="product.price.asc"]',
    )
    PRICES = (By.CSS_SELECTOR, "#js-product-list .product-miniature__price")
    NEXT_PAGE = (By.CSS_SELECTOR, ".next.js-pager-link")

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
                message=f"Could not click {description}.",
            )
        except TimeoutException:
            self.driver.save_screenshot("tc01-click-failure.png")
            raise

    def open_accessories(self):
        self._click(self.ACCESSORIES, "the Accessories category link")
        self.wait.until(EC.visibility_of_element_located(self.CATEGORY_HEADING))

    def category_name(self):
        heading = self.wait.until(
            EC.visibility_of_element_located(self.CATEGORY_HEADING)
        )
        return heading.text.strip().splitlines()[0].strip()

    def sort_by_lowest_price(self):
        if "price, low to high" in self.selected_sort().casefold():
            return

        first_price = self.wait.until(EC.visibility_of_element_located(self.PRICES))
        self._click(self.SORT_BUTTON, "the Sort by dropdown")
        self._click(self.PRICE_LOW_TO_HIGH, "the Price, low to high option")

        self.wait.until(EC.staleness_of(first_price))
        self.wait.until(
            EC.text_to_be_present_in_element(self.SORT_BUTTON, "Price, low to high")
        )

    def selected_sort(self):
        button = self.wait.until(EC.visibility_of_element_located(self.SORT_BUTTON))
        return button.text.strip()

    def prices_on_current_page(self):
        elements = self.wait.until(EC.visibility_of_all_elements_located(self.PRICES))
        return [
            Decimal(re.sub(r"[^\d.]", "", element.text))
            for element in elements
        ]

    def go_to_next_page(self):
        if not self.driver.find_elements(*self.NEXT_PAGE):
            return False

        first_price = self.wait.until(EC.visibility_of_element_located(self.PRICES))
        self._click(self.NEXT_PAGE, "the Next page button")
        self.wait.until(EC.staleness_of(first_price))
        self.wait.until(EC.visibility_of_element_located(self.PRICES))
        return True