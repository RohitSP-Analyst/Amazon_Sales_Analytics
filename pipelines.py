

import os
import re
import csv
import datetime
import logging

logger = logging.getLogger(__name__)


def _to_float(value):
    """Extract a float from a messy price/rating string like '$1,299.00' or '4.5'."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[\d,]+\.?\d*", str(value).replace(",", ""))
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def _to_int(value):
    """Extract an integer from strings like '1,234 ratings' or '2K+ bought'."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    s = str(value).upper().replace(",", "").strip()
    multiplier = 1
    if "K" in s:
        multiplier = 1000
        s = s.replace("K", "")
    elif "M" in s:
        multiplier = 1_000_000
        s = s.replace("M", "")
    match = re.search(r"[\d.]+", s)
    if match:
        try:
            return int(float(match.group()) * multiplier)
        except ValueError:
            return None
    return None


class CleanDataPipeline:
    """Normalizes raw scraped text into clean numeric / consistent fields."""

    def process_item(self, item, spider):
        item["price"] = _to_float(item.get("price"))
        item["original_price"] = _to_float(item.get("original_price"))
        item["rating"] = _to_float(item.get("rating"))
        item["review_count"] = _to_int(item.get("review_count"))
        item["bought_last_month"] = _to_int(item.get("bought_last_month"))

        # Compute discount % if not directly scraped but both prices exist
        if not item.get("discount_percent"):
            price = item.get("price")
            original = item.get("original_price")
            if price and original and original > price:
                item["discount_percent"] = round((1 - price / original) * 100, 2)
            else:
                item["discount_percent"] = 0.0
        else:
            item["discount_percent"] = _to_float(item.get("discount_percent"))

        # Normalize text fields
        for field in ("title", "brand", "availability", "seller", "category"):
            val = item.get(field)
            if val:
                item[field] = re.sub(r"\s+", " ", str(val)).strip()

        item["is_prime"] = bool(item.get("is_prime"))
        item["scraped_at"] = datetime.datetime.utcnow().isoformat()

        return item


class CsvWriterPipeline:
    """Writes all scraped items to a single timestamped CSV file."""

    FIELDNAMES = [
        "asin",
        "title",
        "brand",
        "category",
        "price",
        "currency",
        "original_price",
        "discount_percent",
        "rating",
        "review_count",
        "bought_last_month",
        "availability",
        "is_prime",
        "seller",
        "product_url",
        "image_url",
        "scraped_at",
    ]

    def open_spider(self, spider):
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = os.path.join(output_dir, f"amazon_products_{timestamp}.csv")

        self.file = open(self.filepath, "w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=self.FIELDNAMES)
        self.writer.writeheader()
        logger.info("Writing scraped data to %s", self.filepath)

    def process_item(self, item, spider):
        row = {field: item.get(field, "") for field in self.FIELDNAMES}
        self.writer.writerow(row)
        return item

    def close_spider(self, spider):
        self.file.close()
        logger.info("Finished writing CSV: %s", self.filepath)
