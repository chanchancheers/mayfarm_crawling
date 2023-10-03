import scrapy
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from items import YnanewsscraperItem

class PoliticsSpider(scrapy.Spider):
    name= "Politics"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/politics/president?site=navi_politics_depth02", #대통령실/총리실
            "https://www.yna.co.kr/politics/national-assembly?site=navi_politics_depth02", #국회/정당
            "https://www.yna.co.kr/politics/diplomacy?site=navi_politics_depth02", #외교
            "https://www.yna.co.kr/politics/defense?site=navi_politics_depth02", #국방
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self, response):
        posts = response.css("div.section01 ul.list li div.item-box01")

        for post in posts:
            go_to_post = post.css("div.news-con a").attrib['href']
            yield response.follow(go_to_post, callback=self.parse_post)
        
        #pagination
        page_section = response.css("div.paging")
        current_page = int(page_section.css("strong.num::text").get())

        page_href = page_section.css("")

        next_page_frame = response.url.split("?site")[0]

        next_page = current_page+1

        next_page_url = f"{next_page_frame}/{next_page}"
        if (next_page < 3) :
            yield response.follow(next_page_url, callback=self.parse_list)
        else :
            yield

    def parse_post(self, response):
        item = YnanewsscraperItem()

        
        item['subject'] = response.css("h1.tit::text").get()
        item['created_date'] = response.css("p.update-time::text")[1].get().strip() #yyyy-MM-dd HH:mm
        
        authors = response.css("div.writer-zone01 div.txt-con strong.tit-name::text ")
        authors_list = []
        for author in authors:
            authors_list.append(author.get().strip())
        authors_string = ",,,".join([x for x in authors_list])
        item['author'] = authors_string

        item['headline'] = response.css("div.tit-sub h2.tit::text").get()
        item['img_src'] = response.css("div.img-con span.img img").attrib["src"]
        item['img_alt'] = response.css("div.img-con span.img img").attrib["alt"]
        item['img_desc'] = response.css("p.txt-desc::text").get()
        
        #article
        articles = response.xpath('//*[@id="articleWrap"]/div[2]/div/div/article/p/text()')
        articles_list = []
        for paragraph in articles :
            articles_list.append(paragraph.get().strip())
        item['articles'] = " ".join([x for x in articles_list]).strip()

        #tags
        tags = response.css("ul.list-text01 li a::text")
        tags_list = []
        for tag in tags:
            tags_list.append(tag.get())
        item['tags'] = ",,,".join([x for x in tags_list])
                
        item['depth1'] = response.css("ul.nav-path01 li a::text")[1].get()
        item['depth2'] = response.css("ul.nav-path01 li a::text")[2].get()


        yield item