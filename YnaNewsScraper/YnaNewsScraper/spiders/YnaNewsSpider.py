import scrapy
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from items import YnanewsscraperItem
import logging
from scrapy.utils.log import configure_logging 
import re

class YnaNewsSpider(scrapy.Spider):
    name= "YnaNews"

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log-ERROR.txt',
        format='%(levelname)s: %(message)s',
        level=logging.ERROR,
        encoding='utf-8'
    )


    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/politics/index?site=navi_politics_depth01",
            # "https://www.yna.co.kr/north-korea/all?site=navi_nk_depth01",
            # "https://www.yna.co.kr/economy/index?site=navi_economy_depth01",
            # "https://www.yna.co.kr/industry/index?site=navi_industry_depth01",
            # "https://www.yna.co.kr/society/index?site=navi_society_depth01",
            # "https://www.yna.co.kr/local/index?site=navi_local_depth01",
            # "https://www.yna.co.kr/international/index?site=navi_international_depth01",
            # "https://www.yna.co.kr/culture/index?site=navi_culture_depth01",
            # "https://www.yna.co.kr/lifestyle/index?site=navi_lifestyle_depth01",
            # "https://www.yna.co.kr/entertainment/index?site=navi_entertainment_depth01",
            # "https://www.yna.co.kr/sports/index?site=navi_sports_depth01",
            # "https://www.yna.co.kr/opinion/index?site=navi_opinion_depth01",
            # "https://www.yna.co.kr/people/index?site=navi_people_depth01",

        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)


    def parse_depth1(self, response):
        
        depth1  = response.url.split('/')[3]

        #북한 주제에는 소주제가 없다.

        depth2s = response.css(f"li.depth-box01.{depth1} dd")
        if not depth2s:
            if depth1 in ['opinion', 'visual'] :            #소주제 '전체기사'가 없는 경우
                depth2s =response.css(f"li.depth-box02.{depth1} dd")
            elif depth1 in ['north-korea']:                   #북한인 경우 소주제 자체가 없음
                yield response.follow(response.url, callback=self.parse_list, dont_filter=True)
            else:                                           #소주제가 모두 있고 태그가 없는 경우(사람들 등)
                depth2s = response.css(f"li.depth-box02.{depth1} dd")[1:]

        for depth2 in depth2s:
                go_to_href = depth2.css('a').attrib['href']
                yield response.follow(go_to_href, callback=self.parse_list)
             


            

    def parse_list(self, response):
        posts = response.css("div.section01 div.list-type038 ul.list li div.item-box01")

        for post in posts:
            #Thumbnail 저장해서 박는다.
            item = YnanewsscraperItem()
            
            try :
                thumbnail = ["http:" + post.css("figure.img-con a img").attrib["src"]]
            except:
                thumbnail = []
            item['thumbnail_src'] = thumbnail
            go_to_post = post.css("div.news-con a").attrib['href']
            yield response.follow(go_to_post, callback=self.parse_post, meta={"item_with_thumbnail" : item})
        
        #pagination
        page_section = response.css("div.paging")
        current_page = int(page_section.css("strong.num::text").get())


        next_page_frame = response.url.split("?site")[0]

        next_page = current_page+1

        next_page_url = f"{next_page_frame}/{next_page}"
        if (next_page < 1) :
            yield response.follow(next_page_url, callback=self.parse_list)
        else :
            yield

    def parse_post(self, response):
        item = response.meta.get("item_with_thumbnail")

        item['id'] = response.url.split('/')[4].split('?')[0]
        item['subject'] = response.css("h1.tit::text").get()
        item['created_date'] = response.css("p.update-time::text")[1].get().strip() #yyyy-MM-dd HH:mm
        
        authors = response.css("div.writer-zone01 div.txt-con strong.tit-name::text ")
        if authors:
            authors_list = []
            for author in authors:
                authors_list.append(author.get().strip())
            authors_string = ",,,".join([x for x in authors_list])
            item['author'] = authors_string
        else:
            item['author'] =''
        
        headline = response.css("div.tit-sub h2.tit::text").get()
        if headline != None :
            item['headline'] = response.css("div.tit-sub h2.tit::text").get()
        else :
            item['headline'] = ''
        try :
            item['img_src'] = ["http:" + response.css("div.img-con span.img img").attrib["src"]]
            item['img_alt'] = response.css("div.img-con span.img img").attrib["alt"]
            item['img_desc'] = response.css("p.txt-desc::text").get()
        except:
            item['img_src'] = ''
            item['img_alt'] = ''
            item['img_desc'] = ''
        
        #article
        articles = response.xpath('//*[@id="articleWrap"]/div[2]/div/div/article/p/text()')
        articles_list = []
        for paragraph in articles :
            articles_list.append(re.sub("'", "''", paragraph.get().strip()))
        item['article'] = " ".join([x for x in articles_list]).strip()

        #tags
        tags = response.css("ul.list-text01 li a::text")
        tags_list = []
        for tag in tags:
            tags_list.append(tag.get())
        item['tags'] = ",,,".join([x for x in tags_list])
                
        item['depth1'] = response.xpath('//*[@id="articleWrap"]/div[1]/header/ul[1]/li/*/text()')[1].get()
        
        item['depth2'] = response.xpath('//*[@id="articleWrap"]/div[1]/header/ul[1]/li/*/text()')[2].get()

        yield item