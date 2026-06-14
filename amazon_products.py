

import scrapy
from urllib.parse import quote_plus
from amazon_scraper.items import AmazonProductItem


class AmazonProductsSpider(scrapy.Spider):
    name = "amazon_products"
    allowed_domains = ["amazon.com"]

    custom_settings = {
        
    }

    def __init__(self, keywords="laptop", pages=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keywords = [k.strip() for k in keywords.split(",") if k.strip()]
        self.pages = int(pages)

    def start_requests(self):
        for keyword in self.keywords:
            for page in range(1, self.pages + 1):
                url = (
                    f"https://www.amazon.com/s?k={quote_plus(keyword)}"
                    f"&page={page}"
                )
                yield scrapy.Request(
                    url,
                    callback=self.parse_search_results,
                    meta={"keyword": keyword, "page": page},
                )

    def parse_search_results(self, response):
        keyword = response.meta["keyword"]

        results = response.css('div[data-component-type="s-search-result"]')

        if not results:
            self.logger.warning(
                "No results found on %s — page may be a CAPTCHA/block page "
                "or selectors are outdated. Check output/debug_*.html",
                response.url,
            )
            # Save the page for debugging selector issues
            self._save_debug_page(response, keyword)
            return

        for product in results:
            item = AmazonProductItem()

            item["asin"] = product.attrib.get("data-asin")
            item["category"] = keyword

            item["title"] = product.css(
                "h2 span::text, h2 a span::text"
            ).get()

            item["brand"] = product.css(
                "h2 + div span.a-size-base-plus::text"
            ).get()

            
            price_whole = product.css(".a-price-whole::text").get()
            price_fraction = product.css(".a-price-fraction::text").get()
            if price_whole:
                item["price"] = f"{price_whole}{price_fraction or '00'}".replace(",", "")
            else:
                item["price"] = None

            item["currency"] = "USD"

            item["original_price"] = product.css(
                ".a-price.a-text-price .a-offscreen::text"
            ).get()

            item["rating"] = product.css(
                "span.a-icon-alt::text"
            ).get() 

            item["review_count"] = product.css(
                'span[aria-label][dir="auto"]::text, '
                "a.a-link-normal span.a-size-base::text"
            ).get()

            item["bought_last_month"] = product.css(
                "span.a-size-base.a-color-secondary::text"
            ).get()  

            relative_url = product.css("h2 a::attr(href)").get()
            item["product_url"] = (
                response.urljoin(relative_url) if relative_url else None
            )

            item["image_url"] = product.css("img.s-image::attr(src)").get()

            item["availability"] = "In Stock"  
            item["is_prime"] = bool(
                product.css('i.a-icon-prime, span[aria-label="Amazon Prime"]')
            )
            item["seller"] = None  

            yield item

    def _save_debug_page(self, response, keyword):
        import os
        os.makedirs("output", exist_ok=True)
        safe_keyword = "".join(c if c.isalnum() else "_" for c in keyword)
        path = f"output/debug_{safe_keyword}_{response.meta['page']}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(response.text)
        self.logger.info("Saved debug HTML to %s", path)
