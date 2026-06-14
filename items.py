import scrapy


class AmazonProductItem(scrapy.Item):
    """
    Fields chosen specifically for downstream BI / Power BI analysis:
    - pricing fields support revenue/profitability analysis
    - rating/review fields support customer behavior & sentiment analysis
    - category/brand support segmentation & regional/category trend analysis
    - scraped_at supports time-series trend tracking if scraper is run repeatedly
    """
    asin = scrapy.Field()
    title = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()          # search keyword / category used to find product
    price = scrapy.Field()
    currency = scrapy.Field()
    original_price = scrapy.Field()    # MRP / list price (before discount)
    discount_percent = scrapy.Field()
    rating = scrapy.Field()            # average star rating
    review_count = scrapy.Field()
    availability = scrapy.Field()
    is_prime = scrapy.Field()
    seller = scrapy.Field()
    product_url = scrapy.Field()
    image_url = scrapy.Field()
    bought_last_month = scrapy.Field() 
    scraped_at = scrapy.Field()
