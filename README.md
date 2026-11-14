# QA Assessment – PrestaShop Selenium Tests

Part 1 test cases are in `TC.docx`. Part 2 uses Python, Selenium WebDriver,
pytest and Chrome. Page Objects and locators are in `pages/`, and test
steps and assertions are in `tests/`.

## How to run

Install Python and Google Chrome. Open PowerShell in the repository folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install selenium pytest
$env:SHIRT_URL = "https://dear-ants.demo.prestashop.com/1-hummingbird-printed-t-shirt.html"
.\.venv\Scripts\python.exe -m pytest -v .\tests --tb=short
```

## Test coverage

| Test | What it verifies |
|---|---|
| TC-01 | Accessories are sorted by price from low to high, including across pages when paginated. |
| TC-02 | A search with no matches shows a no-results message and zero products. |
| TC-03 | The T-shirt name and selling price match between the search result and product page. |
| TC-04 | Clicking `+` increases quantity from 1 to 2 and Add to cart stays available. |
| TC-05 | The quantity cannot be decreased below 1. |
| TC-14 | Guest checkout rejects an invalid email and advances to the address step after correction. |
| TC-15 | Add two T-shirts and one mug, verify the cart, and reach the guest checkout Order Summary. |

## Known limitations

- The tests target the English PrestaShop Hummingbird demo. If the demo URL expires,
  set `SHIRT_URL` to the T-shirt product page on an active demo instance.
- TC-15 needs both products in stock, guest checkout enabled, and delivery available
  for the test address. It ends at Order Summary before payment.
- TC-15 allows a €0.01 difference in the T-shirt line total and merchandise subtotal
  comparisons to account for rounding of displayed prices.
- Sticky elements can intercept clicks. The Page Objects use explicit waits and
  retry affected clicks.

## Verified result

All 7 tests passed in a single run on Windows with Python 3.14.3 and Chrome.