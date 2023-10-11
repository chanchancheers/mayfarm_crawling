# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YnanewsscraperItem(scrapy.Item):
    # define the fields for your item here like:
   
    id = scrapy.Field()
    thumbnail_src = scrapy.Field()
    thumbnails = scrapy.Field()

    subject = scrapy.Field()
    created_date = scrapy.Field()
    author = scrapy.Field()
    headline = scrapy.Field()
    img_src = scrapy.Field()
    img_alt = scrapy.Field()
    img_desc = scrapy.Field()
    imgs = scrapy.Field()
    article = scrapy.Field()
    tags = scrapy.Field()
    depth1 = scrapy.Field()
    depth2 = scrapy.Field()
    crawled_date = scrapy.Field()