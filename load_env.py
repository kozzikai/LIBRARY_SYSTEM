import logging
from dotenv import load_dotenv
import os

load_dotenv()  # Loads the .env file's variables

DB_HOST = os.environ.get('DB_HOST')
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_SCHEMA_FILE = os.environ.get('DB_SCHEMA_FILE')
BOOKS_CSV_FILE = os.environ.get('BOOKS_CSV_FILE')
BORROWERS_CSV_FILE = os.environ.get('BORROWERS_CSV_FILE')
DB_NAME = os.environ.get('DB_NAME')
BOOK_TABLE = os.environ.get('BOOK_TABLE')
AUTHOR_TABLE = os.environ.get('AUTHOR_TABLE')
BOOK_AUTHOR_TABLE = os.environ.get('BOOK_AUTHOR_TABLE')
BORROWER_TABLE = os.environ.get('BORROWER_TABLE')
LOANS_TABLE = os.environ.get('LOANS_TABLE')
FINES_TABLE = os.environ.get('FINES_TABLE')

