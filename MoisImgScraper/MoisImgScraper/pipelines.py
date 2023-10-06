# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import hashlib
import pymysql
import scrapy

class MoisimgscraperPipeline:
    def __init__(self):
        self.connection = pymysql.connect(host='localhost', user='sineuncha',password='mayfarm0830@M',db='mois_image', charset='utf8')
        self.cursor = self.connection.cursor()
    
    
    def process_item(self, item, spider):

    
        postQuery = """INSERT INTO post (id, subject, created_date, author, 
                                        contents, crawled_date, thumbnail_src, thumbnail_path) 
                                VALUES (%s,%s,%s,%s,%s,%s, %s, %s)"""
        self.cursor.execute(postQuery, (item['id'], item['subject'], item['created_date'], 
                                        item['author'], item['contents'], item['crawled_date'], 
                                        item['thumbnail_src'], item['thumbnails'][0]['path']))
        
        
        fileQuery = """INSERT INTO file (id, file_sequence, file_name, file_url, file_path)
                                    VALUES (%s, %s, %s, %s, %s)"""
        
        for i, (name, url, path) in enumerate(zip(item['file_names'], item['file_urls'], item['imgs']), start=1):
            self.cursor.execute(fileQuery, (item['id'], i, name, url, path['path']))
        

        # self.connection.commit()
        
        return item
    
    def close_spider(self, spider):
        self.connection.commit()
        self.connection.close()
    

class MyImagePipeline(ImagesPipeline) :
    
    def get_media_requests(self, item, info):
        for idx, file_url in enumerate(item['file_urls']):  # 수집되어야할 파일들의 URL은 반드시 List 자료형으로 입력된다.
            yield scrapy.Request(file_url, meta={'filename': item['file_names'][idx]})
    
    def file_path(self, request, response=None, info=None, *, item=None):
        
        image_name : str = request.meta['filename']
        image_url_hash = hashlib.shake_256(image_name.encode()).hexdigest(5)
        extension = image_name.split('.')[1]
        directory_name = request.url.split("FILE_")[1][:6]

        image_filename = f"{directory_name}/{image_url_hash}.{extension}"
        
        return image_filename

class ThumbnailPipeline(ImagesPipeline) :
    def file_path(self, request, response=None, info=None, *, item=None):
        image_url_hash = hashlib.shake_256(request.url.encode()).hexdigest(5)
        extension = request.url.split('.')[1]
        directory_name = request.url.split("FILE_")[1][:6]

        image_filename = f"thumbnail/{directory_name}/{image_url_hash}.{extension}"
        
        return image_filename