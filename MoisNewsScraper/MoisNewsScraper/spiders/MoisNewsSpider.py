import scrapy
from datetime import datetime
import os
import sys
from scrapy.utils.log import configure_logging 
import logging
import re
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from items import MoisnewsscraperItem

class MoisNewsSpider(scrapy.Spider):
    name = 'MoisNews'
    home_url = "https://www.mois.go.kr"
    response_url = "https://www.mois.go.kr/frt/bbs/type010/commonSelectBoardList.do?bbsId=BBSMSTR_000000000008"
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log-ERROR.txt',
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG,
        encoding='utf-8'
    )

    def start_requests(self) :
        start_urls= [
            "https://www.mois.go.kr/frt/bbs/type010/commonSelectBoardList.do?bbsId=BBSMSTR_000000000008",
        ]
        yield scrapy.Request(url=start_urls[0], callback=self.parse_list)

    def parse_list(self, response):
        postlist = response.css("div.table_wrap table.table_style1 tbody tr")
        for post in postlist:
            go_to_href = post.css("td.l a").attrib['href']
            yield response.follow(go_to_href, callback=self.parse_post)


        pagenate = response.css("div.pagenate")
        last_button_idx = int(pagenate.css("a.last").attrib['href'].split('pageIndex=')[1])
        
        current_page_idx = int(pagenate.css("a.on::text").get().strip('"'))

        next_href = f'{self.response_url}&searchCnd=&searchWrd=&pageIndex={current_page_idx + 1}'

        print("\n\ncurrent_page_index : ", current_page_idx)

        if current_page_idx != last_button_idx :
            yield response.follow(next_href, callback=self.parse_list)
        else :
            yield response.follow(next_href, callback=self.parse_last)



    def parse_post(self, response):
        #제목    
        subject = response.css("h4.subject::text").get().strip()
        if response.css("h4.subject span.sub_desc::text").get() != None :
            subject_desc = response.css("h4.subject span.sub_desc::text").get().strip()
        else :
            subject_desc = ""


        lst = response.xpath('//*[@id="print_area"]/form/div/div[2]/text()')
        lst2 = []
        for a in lst:
            if a.get().strip() != "" :
                lst2.append(a.get().strip())

        created_date = lst2[0].split(":")[1].strip()
        author = lst2[1].split(":")[1].strip()

        content_list = response.xpath('//*[@id="desc_mo"]/text()')
        content_string = " ".join([x.strip() for x in content_list.extract()])
        
        


        # # files_string = ",,,".join([x for x in files])

        # file_names_list = []
        # for i in range(1, len(files)+1) :
        #     file_name = response.xpath(f'//*[@id="print_area"]/form/div[1]/dl[1]/dd/div/ul/li[{i}]/a[1]/text()')[1].get().split()[0]
        #     file_names_list.append(file_name)
        # file_names_string = ",,,".join([x for x in file_names_list])

        file_list = response.css("div.fileList ul li")

        files = []
        for file in file_list:
            file_href = file.css("a").attrib['href']
            files.append(self.home_url + file_href)
            # files.append(file_href)


        filename_list = []
        

        for i in range(1, len(file_list)+1):
            filenames = response.xpath(f'//*[@id="print_area"]/form/div/dl[1]/dd/div/ul/li[{i}]/a[1]/text()')
            filename = "".join([x.get().strip() if x.get().strip() != "" else "" for x in filenames]).split('\n')[0]
            filename_list.append(re.sub(" ", "_", filename))
        
        
        



        crawled_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]

        item = MoisnewsscraperItem()

        id_big = response.url.split("bbsId=")[1]
        id_small = id_big.split("&nttId=")[0] + id_big.split("&nttId=")[1]

        item['id'] = id_small
        item['subject'] = subject
        item['subject_desc'] = subject_desc
        item['created_date'] = created_date
        item['author'] = author
        item['contents'] = content_string
        item['file_urls'] = files
        item['file_names'] = filename_list 
        item['crawled_date'] = crawled_date

        yield item
        
    def parser_last(self, response) :
        postlist = response.css("div.table_wrap table.table_style1 tbody tr")
        for post in postlist:
            go_to_href = post.css("td.l a").attrib['href']
            yield response.follow(go_to_href, callback=self.parse_post)
        print(f"\n\n\nParsing Every Post Done : {datetime.now()}")
        