# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import json
from datetime import datetime
import re
import unicodedata

from itemadapter import ItemAdapter
from scrapy.spiders import Spider
from scrapy.item import Item

from .utils.database_manager import DatabaseManager

DATABASE_HOST = os.environ.get('PCTS_SCRAPERS_RAW_DOCUMENTS_HOST_DB')
DATABASE_NAME = os.environ.get('PCTS_SCRAPERS_RAW_DOCUMENTS_DB')
DATABASE_USER = os.environ.get('PCTS_SCRAPERS_RAW_DOCUMENTS_DB_USER')
DATABASE_PASSWORD = os.environ.get('PCTS_SCRAPERS_RAW_DOCUMENTS_DB_PASS')
DEFAULT_ROOT_OUTPUT_DATA_FOLDER = f"{os.getcwd()}/output_data/"


class SaveGenericPagePipeline:

    def open_spider(self, spider: Spider):
        self.site_name = spider.site_name
        self.keyword = spider.keyword
        self.logger = spider.logger
        self.root_output_data_folder = DEFAULT_ROOT_OUTPUT_DATA_FOLDER
        self.scraper_start_datetime = datetime.now().strftime("%Y%m%d_%H%M")

        try:
            self.db = DatabaseManager(
                DATABASE_HOST,
                DATABASE_NAME,
                credentials={
                    "user": DATABASE_USER,
                    "password": DATABASE_PASSWORD,
                }
            )
        except Exception as e:
            self.logger.error("Error on start DB Client")
            raise e

    def process_item(self, item: Item, spider):
        self.save_page_content(item)

        return item

    def save_page_content(self, item: Item):
        self.db.save(
            self.site_name,
            {
                "source": item["source"],
                "url": item["url"],
                "slug": self.clean_text(item['title']),
                "title": item["title"],
                "content": item["content"],
                "keyword": self.keyword,
            },
            verification_fields={"url"}
        )

    def clean_text(self, text):
        normalized_text = unicodedata.normalize('NFKD', text.lower())\
            .encode('ascii', 'ignore')
        return "_".join(re.findall(
            "\w+",
            normalized_text.decode('ascii'))
        )
