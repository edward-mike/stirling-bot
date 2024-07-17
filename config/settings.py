import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from ._constants import *

load_dotenv()

# Build path inside the project directory
BASE_DIR = Path(__file__).resolve().parent.parent

################################################################
# Logging configuration
################################################################


def setup_logger(log_directory, enable_console=False):

    class CustomFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            return datetime.fromtimestamp(record.created).strftime("%b %d %I:%M:%S %p")

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = os.path.join(log_directory, os.getenv("LOG_FILE", "default.log"))

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        CustomFormatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    logging.basicConfig(level=logging.INFO, handlers=[file_handler])

    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            CustomFormatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(console_handler)


################################################################
# Directory to knowledge files
################################################################

DATA_DIR = os.path.join(BASE_DIR, "data", "v1") # use v1 in Dev. and v2 in Prod.
WEBDATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PDFDATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PREDATA_DIR = os.path.join(BASE_DIR, "data", "preprocessed")
LANGUAGES_PATH = os.path.join(BASE_DIR, "translator", "languages.json")

URLS_FILE = os.path.join(BASE_DIR, "urls.txt")
LOGO_URL = os.path.join(BASE_DIR, "static", "images", "logo.jpg")

PDF_DOC = "files"  # documents
LOG_DIR = "logs"
