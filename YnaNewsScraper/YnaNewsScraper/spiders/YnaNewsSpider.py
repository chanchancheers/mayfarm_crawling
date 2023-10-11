import scrapy
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from items import YnanewsscraperItem
import logging
# from scrapy.utils.log import configure_logging
# from scrapy.crawler import CrawlerProcess
# from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
import re

class YnaNewsSpider(scrapy.Spider):
    name= "YnaNews"
    logging.basicConfig(
        filename='log-ERROR.txt',
        format='%(levelname)s: %(message)s',
        level=logging.ERROR,
        encoding='utf-8'
    )


    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/politics/index?site=navi_politics_depth01",
            "https://www.yna.co.kr/north-korea/all?site=navi_nk_depth01",
            "https://www.yna.co.kr/economy/index?site=navi_economy_depth01",
            "https://www.yna.co.kr/industry/index?site=navi_industry_depth01",
            "https://www.yna.co.kr/society/index?site=navi_society_depth01",
            "https://www.yna.co.kr/local/index?site=navi_local_depth01",
            "https://www.yna.co.kr/international/index?site=navi_international_depth01",
            "https://www.yna.co.kr/culture/index?site=navi_culture_depth01",
            "https://www.yna.co.kr/lifestyle/index?site=navi_lifestyle_depth01",
            "https://www.yna.co.kr/entertainment/index?site=navi_entertainment_depth01",
            "https://www.yna.co.kr/sports/index?site=navi_sports_depth01",
            "https://www.yna.co.kr/opinion/index?site=navi_opinion_depth01",
            "https://www.yna.co.kr/people/index?site=navi_people_depth01",

        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)


    def parse_depth1(self, response):
        
        depth1  = response.url.split('/')[3]

        #북한 주제에는 소주제가 없다.

        depth2s = response.css(f"li.depth-box01.{depth1} dd")
        if not depth2s:
            if depth1 in ['opinion', 'visual'] :            #소주제 '전체기사'가 없는 경우
                do_next =response.css(f"li.depth-box02.{depth1} dd")
                for thing in do_next:
                    go_to_href = thing.css('a').attrib['href']
                    yield response.follow(go_to_href, callback=self.parse_list_first)
            elif depth1 in ['north-korea']:                   #북한인 경우 소주제 자체가 없음
                yield response.follow(response.url, callback=self.parse_list_first, dont_filter=True)
            else:                                           #소주제가 모두 있고 태그가 없는 경우(사람들 등)
                do_next = response.css(f"li.depth-box02.{depth1} dd")[1:]
                for thing in do_next:
                    go_to_href = thing.css('a').attrib['href']
                    yield response.follow(go_to_href, callback=self.parse_list_first)

        else:
            for depth2 in depth2s[1:]:
                go_to_href = depth2.css('a').attrib['href']
                yield response.follow(go_to_href, callback=self.parse_list_first)
             


            
    def parse_list_first(self,response):
        default_url = response.url.split('?site')[0] + '/1'
        yield response.follow(default_url, callback=self.parse_list)



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
            go_to_post = post.css("div.news-con a.tit-wrap").attrib['href']
            yield response.follow(go_to_post, callback=self.parse_post, meta={"item_with_thumbnail" : item})
        
        #pagination
        page_section = response.css("div.paging")
        pages = page_section.css('a')
        current_page = int(response.url.split('/')[-1])
        next_page = "/".join([x for x in response.url.split('/')[:-1]]) + f'/{current_page+1}'
        if int(current_page) != 20 :
            yield response.follow(next_page, callback = self.parse_list)
        else :
            yield response.follow(next_page, callback = self.parse_last)

        # next_page_frame = response.url.split("?site")[0]

        


        # next_page_frames = response.url.split("/")
        # next_page_frame = "/".join([x for x in next_page_frames[:4]])

        # next_page = current_page+1

        # next_page_url = f"{next_page_frame}/{next_page}"
        # if (next_page != 20) :
        #     yield response.follow(next_page_url, callback=self.parse_list)
        # else :
        #     yield response.follow(next_page_url, callback=self.parse_last)

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
        
        
        imgs = response.css("div.comp-box.photo-group")
        if imgs :    
            img_src_list = []
            img_alt_list = []
            img_desc_list = []
            for img in imgs :
                img_src_list.append("http:" + img.css("div.img-con span.img img").attrib['src'])
                img_alt_list.append(img.css("div.img-con span.img img").attrib['alt'])
                img_desc_list.append(img.css('p.txt-desc::text').get())
            item['img_src'] = img_src_list
            item['img_alt'] = img_alt_list
            item['img_desc'] = img_desc_list
        else:
            item['img_src'] = []
            item['img_alt'] = []
            item['img_desc'] = []
        
        #article
        articles = response.xpath('//*[@id="articleWrap"]/div[2]/div/div/article/p/text()')
        articles_list = []
        for paragraph in articles :
            articles_list.append(paragraph.get().strip())
        item['article'] = " ".join([x for x in articles_list]).strip()

        #tags
        tags = response.css("ul.list-text01 li a::text")
        tags_list = []
        for tag in tags:
            tags_list.append(tag.get())
        item['tags'] = ",,,".join([x for x in tags_list])
                
        item['depth1'] = response.xpath('//*[@id="articleWrap"]/div[1]/header/ul[1]/li/*/text()')[1].get()
        
        item['depth2'] = response.xpath('//*[@id="articleWrap"]/div[1]/header/ul[1]/li/*/text()')[2].get()
        item['crawled_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]

        yield item

    def parse_last(self, response):
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
        
        print("One of the Spiders in YnaNews Finished")


class NorthKoreaSpider(YnaNewsSpider) :
    name = "north-korea"

    def start_requests(self):
        start_urls = [
            'https://www.mois.go.kr/frt/bbs/type002/commonSelectBoardList.do?bbsId=BBSMSTR_000000000010',
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class PoliticsSpider(YnaNewsSpider) :
    name = "politics"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/politics/index?site=navi_politics_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class EconomySpider(YnaNewsSpider) :
    name = "economy"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/economy/index?site=navi_economy_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class IndustrySpider(YnaNewsSpider) :
    name = "industry"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/industry/index?site=navi_industry_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class SocietySpider(YnaNewsSpider) :
    name = "society"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/society/index?site=navi_society_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class LocalnewsSpider(YnaNewsSpider) :
    name = "local"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/local/index?site=navi_local_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class InternationalnewsSpider(YnaNewsSpider) :
    name = "international"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/international/index?site=navi_international_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class CultureSpider(YnaNewsSpider) :
    name = "culture"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/culture/index?site=navi_culture_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class LifestyleSpider(YnaNewsSpider) :
    name = "lifestyle"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/lifestyle/index?site=navi_lifestyle_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class EntertainmentSpider(YnaNewsSpider) :
    name = "entertainment"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/entertainment/index?site=navi_entertainment_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class SportsSpider(YnaNewsSpider) :
    name = "sports"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/sports/index?site=navi_sports_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class OpinionSpider(YnaNewsSpider) :
    name = "opinion"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/opinion/index?site=navi_opinion_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class PeopleSpider(YnaNewsSpider) :
    name = "people"

    def start_requests(self):
        start_urls = [
            "https://www.yna.co.kr/people/index?site=navi_people_depth01",
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)

class Spider(YnaNewsSpider) :
    name = ""

    def start_requests(self):
        start_urls = [
    
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_depth1)




# configure_logging()
# runner = CrawlerRunner()

# @defer.inlineCallbacks
# def crawl():
#     yield runner.crawl(NorthKoreaSpider)
#     yield runner.crawl(PoliticsSpider)
#     reactor.stop()
# crawl()
# reactor.run()

# def start_sequentially(process: CrawlerProcess, crawlers: list):
#     print('start crawler {}'.format(crawlers[0].__name__))
#     deferred = process.crawl(crawlers[0])
#     # if len(crawlers) > 1:
#     #     deferred.addCallback(lambda _: start_sequentially(process, crawlers[1:]))


# crawlers = [PoliticsSpider, NorthKoreaSpider]
# process = CrawlerProcess(settings=get_project_settings())
# start_sequentially(process, crawlers)
# process.start()



# settings = get_project_settings()
# process = CrawlerProcess(settings)
# process.crawl(NorthKoreaSpider)
# process.crawl(PoliticsSpider)
# process.crawl(EconomySpider)
# process.crawl(IndustrySpider)
# process.crawl(SocietySpider)
# process.crawl(CultureSpider)
# process.crawl(LifestyleSpider)
# process.crawl(EntertainmentSpider)
# process.crawl(SportsSpider)
# process.crawl(OpinionSpider)
# process.crawl(LocalnewsSpider)
# process.crawl(InternationalnewsSpider)
# process.crawl(PeopleSpider)
# process.start()
