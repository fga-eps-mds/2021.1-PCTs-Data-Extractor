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
import requests

from itemadapter import ItemAdapter
from scrapy.spiders import Spider
from scrapy.item import Item

from .utils.checksum import generate_checksum_from_obj


DOCUMENTS_API_HOST = os.environ.get(
    'PCTS_DOCUMENTS_API_URL', default="http://localhost:8000")
DOCUMENTS_API_ENDPOINT = os.environ.get(
    'PCTS_DOCUMENTS_API_RECORDS_ENDPOINT', default="api/documents/")

DEFAULT_ROOT_OUTPUT_DATA_FOLDER = f"{os.getcwd()}/output_data/"


class SavePageOnDocumentsAPIPipeline:

    def open_spider(self, spider: Spider):
        self.logger = spider.logger
        self.keyword = spider.keyword
        self.stats = spider.crawler.stats
        self.root_output_data_folder = DEFAULT_ROOT_OUTPUT_DATA_FOLDER
        self.scraper_start_datetime = datetime.now().strftime("%Y%m%d_%H%M")
        self.send_document_url = f'{DOCUMENTS_API_HOST}/{DOCUMENTS_API_ENDPOINT}'
        self.request_header = {}

        # Metricas
        self.stats.set_value('saved_records', 0)
        self.stats.set_value('dropped_records', 0)

    def process_item(self, item: Item, spider):
        self.save_page_content(item)

        return item

    def save_page_content(self, item: Item):
        document_page = {
            "source": item["source"],
            "url": item["url"],
            "slug": self.clean_text(item['title']),
            "title": item["title"],
            "content": item["content"],
            "keyword": self.keyword,
            "checksum": generate_checksum_from_obj(item),
            "updated_at": datetime.now().isoformat(),
        }

        response = requests.post(
            url=self.send_document_url,
            headers=self.request_header,
            data=document_page
        )

        if response.status_code == 201:
            self.stats.inc_value('saved_records')
            print("Page Saved:", item["url"])
        else:
            self.stats.inc_value('dropped_records')
            self.logger.error(
                f"Error on Save Page {item['url']}: Error {response.status_code}, ResponseMessage: {response.json()}")

    def clean_text(self, text):
        normalized_text = unicodedata.normalize('NFKD', text.lower())\
            .encode('ascii', 'ignore')
        return "_".join(re.findall(
            "\w+",
            normalized_text.decode('ascii'))
        )


class SavePageOnFilePipeline:

    def open_spider(self, spider: Spider):
        print("NOME DO SITE:", spider.source_name)
        self.source_name = spider.source_name
        self.logger = spider.logger
        self.root_output_data_folder = DEFAULT_ROOT_OUTPUT_DATA_FOLDER
        self.scraper_start_datetime = datetime.now().strftime("%Y%m%d_%H%M")

        self.output_folder_path = os.path.join(
            self.root_output_data_folder,
            self.source_name,
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
