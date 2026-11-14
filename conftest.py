import os

import pytest
from selenium import webdriver

from pages.product_page import ProductPage
from pages.search_page import SearchPage


@pytest.fixture
def storefront_driver():
    url = os.getenv("SHIRT_URL")
    if not url:
        pytest.fail("Set SHIRT_URL to the T-shirt product page URL.")

    with webdriver.Chrome() as driver:
        driver.maximize_window()
        driver.get(url)
        yield driver


@pytest.fixture
def shirt_page(storefront_driver):
    return ProductPage(storefront_driver)


@pytest.fixture
def search_page(storefront_driver):
    return SearchPage(storefront_driver)