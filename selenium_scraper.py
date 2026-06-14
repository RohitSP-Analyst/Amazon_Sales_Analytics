

import os
import re
import csv
import time
import random
import datetime
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)



KEYWORDS = ["laptop", "wireless earbuds", "office chair", "smart watch", "bluetooth speaker"]
PAGES_PER_KEYWORD = 2         
HEADLESS = True               
MIN_DELAY = 4                 
MAX_DELAY = 9
# --------------------------------------------------------------------------


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


def build_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # Reduce obvious automation fingerprints
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Hide navigator.webdriver flag
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


def to_float(text):
    if not text:
        return None
    match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return float(match.group()) if match else None


def to_int(text):
    if not text:
        return None
    text = text.upper().replace(",", "")
    multiplier = 1
    if "K" in text:
        multiplier = 1000
        text = text.replace("K", "")
    elif "M" in text:
        multiplier = 1_000_000
        text = text.replace("M", "")
    match = re.search(r"[\d.]+", text)
    return int(float(match.group()) * multiplier) if match else None


def parse_results_page(driver, keyword):
    items = []
    cards = driver.find_elements(
        By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]'
    )

    if not cards:
        logger.warning("No product cards found for '%s' — possible CAPTCHA/block.", keyword)
        return items

    for card in cards:
        try:
            asin = card.get_attribute("data-asin") or None

            try:
                title = card.find_element(By.CSS_SELECTOR, "h2 span").text.strip()
            except NoSuchElementException:
                title = None

            try:
                price_whole = card.find_element(By.CSS_SELECTOR, ".a-price-whole").text
                try:
                    price_fraction = card.find_element(By.CSS_SELECTOR, ".a-price-fraction").text
                except NoSuchElementException:
                    price_fraction = "00"
                price = to_float(f"{price_whole}.{price_fraction}")
            except NoSuchElementException:
                price = None

            try:
                original_price = to_float(
                    card.find_element(
                        By.CSS_SELECTOR, ".a-price.a-text-price .a-offscreen"
                    ).get_attribute("textContent")
                )
            except NoSuchElementException:
                original_price = None

            try:
                rating_text = card.find_element(By.CSS_SELECTOR, "span.a-icon-alt").get_attribute(
                    "textContent"
                )
                rating = to_float(rating_text)
            except NoSuchElementException:
                rating = None

            try:
                review_text = card.find_element(
                    By.CSS_SELECTOR, 'a.a-link-normal span.a-size-base'
                ).text
                review_count = to_int(review_text)
            except NoSuchElementException:
                review_count = None

            try:
                bought_text = card.find_element(
                    By.CSS_SELECTOR, "span.a-size-base.a-color-secondary"
                ).text
                bought_last_month = to_int(bought_text) if "bought" in bought_text.lower() else None
            except NoSuchElementException:
                bought_last_month = None

            try:
                link = card.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
            except NoSuchElementException:
                link = None

            try:
                image_url = card.find_element(By.CSS_SELECTOR, "img.s-image").get_attribute("src")
            except NoSuchElementException:
                image_url = None

            is_prime = bool(card.find_elements(By.CSS_SELECTOR, 'i.a-icon-prime'))

            discount_percent = 0.0
            if price and original_price and original_price > price:
                discount_percent = round((1 - price / original_price) * 100, 2)

            items.append({
                "asin": asin,
                "title": title,
                "brand": None,
                "category": keyword,
                "price": price,
                "currency": "USD",
                "original_price": original_price,
                "discount_percent": discount_percent,
                "rating": rating,
                "review_count": review_count,
                "bought_last_month": bought_last_month,
                "availability": "In Stock",
                "is_prime": is_prime,
                "seller": None,
                "product_url": link,
                "image_url": image_url,
                "scraped_at": datetime.datetime.utcnow().isoformat(),
            })
        except Exception as e:
            logger.error("Error parsing a product card: %s", e)
            continue

    return items


def main():
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join("output", f"amazon_selenium_{timestamp}.csv")

    fieldnames = [
        "asin", "title", "brand", "category", "price", "currency",
        "original_price", "discount_percent", "rating", "review_count",
        "bought_last_month", "availability", "is_prime", "seller",
        "product_url", "image_url", "scraped_at",
    ]

    driver = build_driver()
    all_items = []

    try:
        for keyword in KEYWORDS:
            for page in range(1, PAGES_PER_KEYWORD + 1):
                url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}&page={page}"
                logger.info("Loading: %s", url)

                driver.get(url)

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')
                        )
                    )
                except TimeoutException:
                    logger.warning(
                        "Timed out waiting for results on '%s' page %d — "
                        "possible CAPTCHA page. Saving HTML for inspection.",
                        keyword, page,
                    )
                    debug_path = os.path.join(
                        "output", f"debug_{keyword.replace(' ', '_')}_{page}.html"
                    )
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    continue

                page_items = parse_results_page(driver, keyword)
                logger.info("Found %d items for '%s' page %d", len(page_items), keyword, page)
                all_items.extend(page_items)

                # Polite randomized delay between requests
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                logger.info("Sleeping %.1f seconds...", delay)
                time.sleep(delay)
    finally:
        driver.quit()

    # Write CSV
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in all_items:
            writer.writerow(item)

    logger.info("Saved %d total items to %s", len(all_items), out_path)


if __name__ == "__main__":
    main()
