# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MoisnewsscraperItem(scrapy.Item):
    id = scrapy.Field()
    subject = scrapy.Field()
    subject_desc = scrapy.Field()
    created_date = scrapy.Field()
    author = scrapy.Field()
    contents = scrapy.Field()
    file_urls = scrapy.Field()
    file_names = scrapy.Field()
    crawled_date = scrapy.Field() 
    file_results = scrapy.Field() 