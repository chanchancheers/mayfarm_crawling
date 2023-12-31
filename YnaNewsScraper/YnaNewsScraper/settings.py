# Scrapy settings for YnaNewsScraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "YnaNewsScraper"

SPIDER_MODULES = ["YnaNewsScraper.spiders"]
NEWSPIDER_MODULE = "YnaNewsScraper.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.24) Gecko/20111109 CentOS/3.6.24-3.el6.centos Firefox/47.0'
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   'YnaNewsScraper.middlewares.YnanewsscraperDeltaFetchSpiderMiddleware' : 100,
   "YnaNewsScraper.middlewares.YnanewsscraperSpiderMiddleware": 543,

}
DELTAFETCH_ENABLED = True
DELTAFETCH_DIR = "delta"

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "YnaNewsScraper.middlewares.YnanewsscraperDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html




ITEM_PIPELINES = {
   "YnaNewsScraper.pipelines.ThumbnailPipeline" : 10,
   "YnaNewsScraper.pipelines.MyImagePipeline" : 50,
   "YnaNewsScraper.pipelines.YnanewsscraperPipeline": 303,
}
# THUMBNAILPIPELINE_IMAGES_STORE = "thumbnails"
# THUMBNAILPIPELINE__DOWNLOAD_DELAY = 0.5
# THUMBNAILPIPELINE_IMAGES_URLS_FIELD = "thumbnail_src"
# THUMBNAILPIPELINE_IMAGES_RESULT_FIELD = "thumbnails"

IMAGES_STORE = "/root/crawled_data/yna/images"
DOWNLOAD_DELAY = 0.5
IMAGES_URLS_FIELD = "thumbnail_src"
IMAGES_RESULT_FIELD = "thumbnails"


MYIMAGEPIPELINE_IMAGES_STORE = "/root/crawled_data/yna/images"
MYIMAGEPIPELINE_DOWNLOAD_DELAY = 0.5
MYIMAGEPIPELINE_IMAGES_URLS_FIELD = "img_src"
MYIMAGEPIPELINE_IMAGES_RESULT_FIELD = "imgs"





# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
