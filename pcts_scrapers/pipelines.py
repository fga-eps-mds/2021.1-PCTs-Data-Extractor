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

DEFAULT_ROOT_OUTPUT_DATA_FOLDER = f"{os.getcwd()}/output_data/"


class SaveGenericPagePipeline:

    def open_spider(self, spider: Spider):
        print("NOME DO SITE:", spider.site_name)
        self.site_name = spider.site_name
        self.logger = spider.logger
        self.root_output_data_folder = DEFAULT_ROOT_OUTPUT_DATA_FOLDER
        self.scraper_start_datetime = datetime.now().strftime("%Y%m%d_%H%M")

        self.output_folder_path = os.path.join(
            self.root_output_data_folder,
            self.site_name,
            self.scraper_start_datetime,
        )

        self.create_directory_structure()

    def process_item(self, item: Item, spider):
        self.save_page_content(item)

        return item

    def create_directory_structure(self):
        if not os.path.exists(self.output_folder_path):
            os.makedirs(self.output_folder_path)

    def save_page_content(self, item: Item):
        current_time = datetime.now().strftime("%H%M%S_%f")
        page_title = self.clean_text(item['title'])
        file_path = os.path.join(
            self.output_folder_path,
            f"{page_title}_{current_time}.json"
        )
        
        item.__dict__
        try:
            with open(file_path, "w", encoding="utf-8") as page_content_f:
                content = {
                    "source": item["source"],
                    "url": item["url"],
                    "title": item["title"],
                    "content": item["content"],
                    "updated_at": int(datetime.now().timestamp()),
                }
                page_content_f.write(json.dumps(content, ensure_ascii=False))
        except Exception as e:
            self.logger.error(
                "Falha ao Carregar Arquivo de Saida: %s",
                page_title
            )
            self.logger.error("Erro:", str(e))

    def clean_text(self, text):
        normalized_text = unicodedata.normalize('NFKD', text.lower())\
            .encode('ascii', 'ignore')
        return "_".join(re.findall(
            "\w+",
            normalized_text.decode('ascii'))
        )
