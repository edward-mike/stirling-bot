import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Build path inside the project directory
BASE_DIR = Path(__file__).resolve().parent.parent

################################################################
# Logging configuration
################################################################


def setup_logger(log_directory, enable_console=False):
    
    class CustomFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            return datetime.fromtimestamp(record.created).strftime('%b %d %I:%M:%S %p')

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = os.path.join(log_directory, os.getenv("LOG_FILE", "default.log"))
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(CustomFormatter("%(asctime)s - %(levelname)s - %(message)s"))

    logging.basicConfig(level=logging.INFO, handlers=[file_handler])
    
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(CustomFormatter("%(asctime)s - %(levelname)s - %(message)s"))
        logging.getLogger().addHandler(console_handler)


################################################################
# Directory to knowledge files
################################################################

DATA_DIR = os.path.join(BASE_DIR, "data", "v1")
WEBDATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PDFDATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PREDATA_DIR = os.path.join(BASE_DIR, "data", "preprocessed")
LANGUAGES_PATH = os.path.join(BASE_DIR, "translator", "languages.json")

URLS_FILE = os.path.join(BASE_DIR, "urls.txt")
LOGO_URL = os.path.join(BASE_DIR, "static", "images", "logo.jpg")

PDF_DOC = "files"  # documents
LOG_DIR = "logs"

################################################################
# Paremeters for Extractions and QnA Generation
################################################################
ALLOW_PDF_EXTRACTION = False  # Set to True to enable PDF extraction
ALLOW_URL_EXTRACTION = False  # Set to True to enable web content extraction
ALLOW_QA_GENERATOR = False  # Set to True to enable QA generation from extracted data

################################################################
# https://python.langchain.com/v0.2/docs/how_to/recursive_text_splitter/
# App config.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 0
DOCUMENTS_RETURN_COUNT = 5