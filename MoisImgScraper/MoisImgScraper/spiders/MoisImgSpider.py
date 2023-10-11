import scrapy
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from items import MoisimgscraperItem

class MoisImgSpider(scrapy.Spider):
    name = "MoisImg"
    home_url = "https://www.mois.go.kr"
    response_url = "https://www.mois.go.kr/frt/bbs/type002/commonSelectBoardList.do?bbsId=BBSMSTR_000000000010"
    def start_requests(self):

        start_urls = [
            "https://www.mois.go.kr/frt/bbs/type002/commonSelectBoardList.do?bbsId=BBSMSTR_000000000010"

        ]
        yield scrapy.Request(url=start_urls[0], callback=self.parse)
    

    def parse(self, response):
        
        for image in response.css("ul.img_gallery_list li"):
            item = MoisimgscraperItem()
            thumbnail = image.css("img").attrib['src']
            item['thumbnail_src'] = [self.home_url + thumbnail]
            post_href = image.css("li a").attrib['href']
            yield response.follow(post_href, callback=self.parse_post, meta={"item_with_thumbnail" : item})
        
        # 아래는 페이지네이션 로직(구현완료)
        pagenate = response.css("div.pagenate")
        last_button_idx = int(pagenate.css("a.last").attrib['href'].split('pageIndex=')[1])
        
        current_page_idx = int(pagenate.css("a.on::text").get().strip('"'))

        next_href = f'{self.response_url}&searchCnd=&searchWrd=&pageIndex={current_page_idx + 1}'

        print("\n\ncurrent_page_index : ", current_page_idx)

        if current_page_idx != last_button_idx :
            yield response.follow(next_href, callback=self.parse)
        else :
            yield response.follow(next_href, callback=self.parse_last)
        
        # page_cnt = len(pagenate.css("span a"))

        # current_on_idx = current_page_idx % 10

        # if (current_on_idx != page_cnt) and (current_on_idx  != 0) :
        #     print("\n\nin the if - current_on_idx : ", current_on_idx)
        #     page_idx_list = pagenate.css("span a")
        #     goto_page_href = page_idx_list[int(current_on_idx)].css('a').attrib['href']
        #     yield response.follow(goto_page_href, callback=self.parse)
        # else :
        #     if (current_page_idx != last_button_idx ) :
        #         print("\n\nin the else - current_on_idx : ", current_on_idx)
        #         yield response.follow(next_href, callback=self.parse)
        #     else :
        #         yield response.follow(next_href, callback=self.parse_last)

        
    def parse_post(self, response) :
        
        subject = response.css("h4.subject::text").get()
        created_date = response.xpath('//*[@id="print_area"]/form/div[1]/div[2]/span[1]/text()').get().split(":")[1].strip()
        author = response.xpath('//*[@id="print_area"]/form/div[1]/div[2]/span[2]/text()').get().split(":")[1].strip()
        
        
        card_news = response.css("div.card_news_slider_wrap ul li")
        img_src_list = []
        
        content_list = []
        for section in card_news:
            image_src = section.css("img").attrib['src']
            img_src_list.append(image_src)

            content = section.css("img").attrib['alt']
            content_list.append(content)

        img_srcs_string = ",,,".join([x for x in img_src_list])
        contents_string = ",,,".join([x for x  in content_list])

        file_list = response.css("div.fileList ul li")

        files = []
        for file in file_list:
            file_href = file.css("a").attrib['href']
            files.append(self.home_url + file_href)
        # files_string = ",,,".join([x for x in files])

        file_names_list = []
        for i in range(1, len(files)+1) :
            file_name = response.xpath(f'//*[@id="print_area"]/form/div[1]/dl[1]/dd/div/ul/li[{i}]/a[1]/text()')[1].get().split()[0]
            file_names_list.append(file_name)
        # file_names_string = ",,,".join([x for x in file_names_list])

        item = response.meta.get('item_with_thumbnail')

        id_big = response.url.split("bbsId=")[1]
        id_small = id_big.split("&nttId=")[0] + id_big.split("&nttId=")[1]

        item['id'] = id_small
        item['subject'] = subject
        item['created_date'] = created_date
        item['author'] = author
        item['contents'] = contents_string
        item['file_urls'] = files
        item['file_names'] = file_names_list
        item['crawled_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]

        yield item

        
    def parse_last(self, response) :
        for image in response.css("ul.img_gallery_list li"):
            item = MoisimgscraperItem()
            thumbnail = image.css("img").attrib['src']
            item['thumbnail_src'] = [self.home_url + thumbnail]
            post_href = image.css("li a").attrib['href']
            yield response.follow(post_href, callback=self.parse_post, meta={"item_with_thumbnail" : item})
        print(f"\n\n\nParsing Every Post Done : {datetime.now()}")