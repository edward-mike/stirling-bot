from configparser import ConfigParser
from typing import List

from config.settings import (  # ALLOW_PDF_EXTRACTION,; ALLOW_QA_GENERATOR,; ALLOW_URL_EXTRACTION,
    PDF_DOC,
    PREDATA_DIR,
    URLS_FILE,
    WEBDATA_DIR,
)
from pipeline import (
    extract_contents_for,
    extract_text_from_pdfs_in_directory,
    preprocess_files,
)

config = ConfigParser()
config.read("config.ini")

# ToDO🤔, Well, I have a life 😂. Never mind:
# UnicodeError when preprocessing extracted pdf files with GPT
# Maximum GPT token length error for large text extraction.


def load_urls() -> List[str]:
    with open(URLS_FILE, "r") as f:
        url = [line.strip() for line in f if line.strip()]
    return url


def run_new() -> None:

    if config.getboolean("DEFAULT", "enable_pdf_extraction"):
        extract_text_from_pdfs_in_directory(PDF_DOC)

    if config.getboolean("DEFAULT", "enable_url_extraction"):
        urls = load_urls()
        extract_contents_for(urls)

    if config.getboolean("DEFAULT", "enable_qa_generator"):
        preprocess_files(WEBDATA_DIR, PREDATA_DIR)
