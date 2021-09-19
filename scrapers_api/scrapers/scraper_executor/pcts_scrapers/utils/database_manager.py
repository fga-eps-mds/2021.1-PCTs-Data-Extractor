import json
import urllib.parse
import hashlib
import pickle
from time import time
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.collection import Collection


class DatabaseManager:

    _db_client = None
    _database = None

    def __init__(self, host, database, credentials):
        print("TRYING CONNECT TO DB")
        username = urllib.parse.quote_plus(credentials["user"])
        password = urllib.parse.quote_plus(credentials["password"])
        self._db_client = MongoClient(
            f"mongodb://{username}:{password}@{host}")
        self._database = self._db_client[database]

        self._db_client.server_info()
        print("DB CONECTED")

    def save(
        self, collection_name: str, document: dict, verification_fields: set = {}
    ) -> ObjectId:
        """Save or replace data
        Args:
            collection_name (str):   collecction in database
            document (dict):    data to be saved
            verification_fields (set): fields to check if document already exists
        """

        try:
            return self._save_document(
                self._database[collection_name], document, verification_fields
            )
        except Exception as e:
            print("Could not save data")
            print(e)
            return None

    def save_list(self, collection_name, document_list, verification_fields: set = {}):
        try:
            collection = self._database[collection_name]
            for document in document_list:
                self._save_document(collection, document, verification_fields)
        except Exception as e:
            print("Could not save data list")
            print(e)

    def _save_document(self, collection: Collection, document, verification_fields) -> ObjectId:
        query = self._build_fields_check_query(verification_fields, document)
        current_doc = None

        if verification_fields:
            try:
                current_doc = collection.find_one(query)
            except Exception:
                pass

        document["checksum"] = self._generate_data_checksum(document)
        document["updated_at"] = round(time())

        print("QUERY:", query)

        collection.replace_one(query, document, upsert=True)

    def _build_fields_check_query(self, fields: set, document: dict):
        query = {}
        for field in fields:
            query[field] = document[field]
        return query

    def _check_data_changed(self, document_ref, new_data) -> bool:
        current_record = document_ref.get().to_dict()

        return current_record["checksum"] != new_data["checksum"]

    def get(self, collection_name: str, query={}, fields=None) -> dict:
        collection = self._database[collection_name]
        return collection.find_one(query, fields)

    def get_list(self, collection_name: str, query={}, fields=None) -> Cursor:
        collection = self._database[collection_name]
        return collection.find(query, fields)

    def get_list_field_list(
        self, collection_name, search_field="_id", values: list = [], fields=None
    ):
        collection = self._database[collection_name]
        if values and len(values):
            return collection.find({search_field: {"$in": list(values)}}, fields)
        return []

    def count(self, collection_name: str, query) -> int:
        collection = self._database[collection_name]
        return collection.count(query)

    def _generate_data_checksum(self, document: dict) -> str:
        try:
            document.pop("_id")
            document.pop("updated_at")
        except Exception:
            pass
        return hashlib.md5(pickle.dumps(sorted(document.items()))).hexdigest()
