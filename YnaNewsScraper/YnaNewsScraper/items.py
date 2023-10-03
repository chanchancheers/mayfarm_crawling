# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YnanewsscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # title = response.css("h1.tit::text").get()
    #     created_date = response.css("p.update-time::text")[1].get().strip() #yyyy-MM-dd HH:mm
    #     author = response.css("strong.tit-name::text").get()
    #     headline = response.css("h2.tit::text").get()
    #     img_src = response.css("div.img-con span.img img").attrib["src"]
    #     img_alt = response.css("div.img-con span.img img").attrib["alt"]
    #     img_desc = response.
    subject = scrapy.Field()
    created_date = scrapy.Field()
    author = scrapy.Field()
    headline = scrapy.Field()
    img_src = scrapy.Field()
    img_alt = scrapy.Field()
    img_desc = scrapy.Field()
    articles = scrapy.Field()
    tags = scrapy.Field()
    depth1 = scrapy.Field()
    depth2 = scrapy.Field()