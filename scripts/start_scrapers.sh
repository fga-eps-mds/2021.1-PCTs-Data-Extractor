#!/bin/bash

export PCTS_DOCUMENTS_API_URL=http://127.0.0.1:8000
export PCTS_DOCUMENTS_API_RECORDS_ENDPOINT=documents/documents/

python crawler_executor.py
