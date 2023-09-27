# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MoisimgscraperItem(scrapy.Item):
    id  = scrapy.Field()
    subject = scrapy.Field()
    created_date = scrapy.Field()
    author = scrapy.Field()
    crawled_date = scrapy.Field()
    contents = scrapy.Field()
    files = scrapy.Field()
    file_names = scrapy.Field()
