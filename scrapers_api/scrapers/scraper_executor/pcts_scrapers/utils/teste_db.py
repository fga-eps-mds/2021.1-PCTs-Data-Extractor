import os
from datetime import datetime

from database_manager import DatabaseManager


os.environ["PCTS_SCRAPERS_RAW_DOCUMENTS_DB"] = "pcts_raw_documents"
os.environ["PCTS_SCRAPERS_RAW_DOCUMENTS_HOST_DB"] = "localhost:27017"

DATABASE_NAME = os.environ.get('PCTS_SCRAPERS_RAW_DOCUMENTS_DB')
DATABASE_HOST = os.environ.get('PCTS_SCRAPERS_RAW_DOCUMENTS_HOST_DB')

credentials = {
    "user": "root",
    "password": "pass12345",
}

db = DatabaseManager(DATABASE_HOST, DATABASE_NAME, credentials)

db.save(
    "tcu",
    {
        "url": "tcu.gov.br",
        "title": "Jurispudencia",
        "body": "<html>BODY</html>",
    },
    verification_fields={"url"}
)
