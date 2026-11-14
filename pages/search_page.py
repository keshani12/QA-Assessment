from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class SearchPage:
    SEARCH_INPUT = (By.CSS_SELECTOR, 'input[name="s"]')
    RESULTS_HEADING = (By.ID, "js-product-list-header")
    PRODUCT_CARDS = (By.CSS_SELECTOR, "#js-product-list .product-miniature")
    CARD_NAME = (By.CSS_SELECTOR, "a.product-miniature__title")
    CARD_PRICE = (By.CSS_SELECTOR, ".product-miniature__price")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def search(self, term):
        search_input = self.wait.until(
            EC.element_to_be_clickable(self.SEARCH_INPUT)
        )
        search_input.clear()
        search_input.send_keys(term, Keys.ENTER)

    def results_heading(self):
        return self.wait.until(
            EC.visibility_of_element_located(self.RESULTS_HEADING)
        ).text

    def product_count(self):
        return len(self.driver.find_elements(*self.PRODUCT_CARDS))

    def open_product_from_results(self, product_name):
        def find_matching_card(driver):
            for card in driver.find_elements(*self.PRODUCT_CARDS):
                link = card.find_element(*self.CARD_NAME)
                name = link.text.strip()
                if name.casefold() == product_name.casefold() and link.is_displayed():
                    price = card.find_element(*self.CARD_PRICE).text.strip()
                    if price:
                        return link, name, price
            return False

        link, name, price = self.wait.until(
            find_matching_card,
            message=f"Could not find {product_name} with a price in the results.",
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
            link,
        )
        link.click()
        return name, price