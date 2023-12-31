# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
import pymysql
from scrapy.pipelines.images import ImagesPipeline
import hashlib
from scrapy.utils.project import get_project_settings

class YnanewsscraperPipeline:

    count = 0

    def __init__(self):
        self.connection = pymysql.connect(host='localhost', user='sineuncha',password='mayfarm0830@M',db='yna_news', charset='utf8')
        self.cursor = self.connection.cursor()


    def process_item(self, item, spider):
        newsQuery = '''INSERT INTO news (id, subject, created_date, author, headline, article, 
                                        tags, depth1, depth2, thumbnail_src, thumbnail_path, crawled_date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        # try : #이미지가 있다
        if (item['img_src']) :
            self.cursor.execute(newsQuery, (item['id'], item['subject'], item['created_date'], item['author'], 
                                        item['headline'], item['article'], item['tags'], 
                                        item['depth1'], item['depth2'],
                                        item['thumbnail_src'], item['thumbnails'][0]['path'],
                                        item['crawled_date']))
        
        
            imageQuery = "INSERT INTO image (id, file_sequence, img_src, img_alt, img_desc, img_path) VALUES (%s, %s, %s, %s, %s, %s)"
            for i, (src, alt, desc, path) in enumerate(zip(item['img_src'], item['img_alt'], item['img_desc'], item['imgs']), start=1):
                self.cursor.execute(imageQuery, (item['id'], i, src, alt, desc, path['path']))


        else : #이미지가 없다
            noImageQuery = """INSERT INTO news (id, subject, created_date, author, headline, article, tags, depth1, depth2,  crawled_date)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(noImageQuery, (item['id'], item['subject'], item['created_date'], item['author'], item['headline'], 
                                                item['article'], item['tags'], item['depth1'], item['depth2'], item['crawled_date']))
        self.count += 1
        if self.count > 100 :
            self.connection.commit()
            self.count = 0

        return item
    
    def close_spider(self, spider):
        self.connection.commit()
        self.connection.close()

class MyImagePipeline(ImagesPipeline) :
    # def get_media_requests(self, item, info):
    #     for idx, file_url in enumerate(item['img_src']):  # 수집되어야할 파일들의 URL은 반드시 List 자료형으로 입력된다.
    #         yield scrapy.Request(file_url, meta={'filename': item['img_src'][idx]})
    def file_path(self, request, response=None, info=None, *, item=None):

        print("\n\n", request.url,"\n\n")

        image_url_hash = hashlib.shake_256(request.url.encode()).hexdigest(5)
        image_perspective = request.url.split("/")[-1]
        extension = request.url.split('.')[-1]
        directory_name = image_perspective[:3]
        image_filename = f"{directory_name}/{image_url_hash}.{extension}"
        
        return image_filename

class ThumbnailPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        image_url_hash = hashlib.shake_256(request.url.encode()).hexdigest(5)
        image_perspective = request.url.split("/")[-1]
        extension = request.url.split('.')[-1]
        directory_name = image_perspective[:3]
        image_filename = f"thumbnail/{directory_name}/{image_url_hash}.{extension}"
        
        return image_filename