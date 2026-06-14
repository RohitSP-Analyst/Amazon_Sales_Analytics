

BOT_NAME = "amazon_scraper"

SPIDER_MODULES = ["amazon_scraper.spiders"]
NEWSPIDER_MODULE = "amazon_scraper.spiders"


ROBOTSTXT_OBEY = False

# --- Concurrency / Throttling (critical for avoiding blocks) ---
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 3              # base delay between requests (seconds)
RANDOMIZE_DOWNLOAD_DELAY = True # randomizes delay between 0.5x - 1.5x of DOWNLOAD_DELAY

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 3
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# --- Retries ---
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 503]

# --- Default request headers (look like a real Chrome browser) ---
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

# --- Middlewares ---
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "amazon_scraper.middlewares.RotateUserAgentMiddleware": 400,
    "amazon_scraper.middlewares.CaptchaDetectionMiddleware": 543,
    
}

# --- Item pipelines ---
ITEM_PIPELINES = {
    "amazon_scraper.pipelines.CleanDataPipeline": 300,
    "amazon_scraper.pipelines.CsvWriterPipeline": 400,
}

# --- Output ---
FEED_EXPORT_ENCODING = "utf-8"

# Logging
LOG_LEVEL = "INFO"

# Set a reasonable timeout
DOWNLOAD_TIMEOUT = 20
