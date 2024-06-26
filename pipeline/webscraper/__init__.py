import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup

from config.settings import LOG_DIR, WEBDATA_DIR, setup_logger
from utils import time_execution

setup_logger(LOG_DIR)


# SCRAP_TO = "uncknowledge"


def is_navigation_or_footer_element(tag):

    common_navigation_classes = ["navbar", "nav", "menu", "navigation", "header"]
    common_footer_classes = ["footer", "footer-wrapper", "footer-container"]

    return (
        tag.name == "nav"
        or tag.has_attr("class")
        and any(cls in tag["class"] for cls in common_navigation_classes)
        or tag.name == "footer"
        or tag.has_attr("class")
        and any(cls in tag["class"] for cls in common_footer_classes)
    )


def exclude_button_text(tag):
    """
    Excludes text content within elements containing the CSS class "button".
    """

    if tag.name != "button" and (
        not tag.has_attr("class") or "button" not in tag["class"]
    ):
        return tag
    else:
        tag.string = ""
        return tag


def exclude_anchor_text(tag):
    """
    Excludes text content within anchor (hyperlink) elements.
    """

    if tag.name != "a":
        return tag
    else:
        tag.string = ""
        return tag


def clean(text):
    # Remove lines starting with "loading..." or "site search"
    text = [
        line
        for line in text.splitlines()
        if not (line.lower().startswith("loading...") or line.lower() == "site search")
    ]
    text = "\n".join(text)
    # regex pattern to match "| about |" or "| home |"
    pattern = r"\|.*?\|"
    # Remove paragraphs containing "| about |" or "| home |"
    text = re.sub(pattern, "", text)
    return text


@time_execution
def extract_text_from_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Exclude navigation, footer, and button elements
        navigation_or_footer_elements = soup.find_all(is_navigation_or_footer_element)
        for elem in navigation_or_footer_elements:
            elem.extract()

        button_elements = soup.find_all(
            lambda tag: tag.name != "button"
            and (not tag.has_attr("class") or "button" not in tag["class"])
        )
        for button in button_elements:
            exclude_button_text(button)

        anchor_elements = soup.find_all(exclude_anchor_text)
        for anchor in anchor_elements:
            exclude_anchor_text(anchor)

        extracted_text = soup.get_text(separator="\n", strip=True)

        # clean text
        extracted_text = extracted_text.lower()
        extracted_text = clean(extracted_text)

        logging.info(f"Extracted text from url: {url}")

        return extracted_text

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve content from {url}: {e}")
        return None


def extract_texts_from_multiple_webpages(urls):
    """
    Extracts text from multiple webpages concurrently.
    """

    with ThreadPoolExecutor() as executor:
        results = executor.map(extract_text_from_webpage, urls)
        return dict(zip(urls, results))


def generate_filename_from_url(url):
    parsed_url = urlparse(url)
    filename = unquote(parsed_url.path)
    filename = filename.strip("/")
    filename = filename.replace("/", "_")
    filename = filename.replace("-", "_")
    if not filename:
        filename = "index"
    return filename + ".txt"


def save_extracted_texts(extracted_texts):
    if extracted_texts:
        # data_dir = os.path.join(os.getcwd(), SCRAP_TO)
        # data_dir = WEBDATA_DIR
        os.makedirs(WEBDATA_DIR, exist_ok=True)
        web_contents_dir = os.path.join(WEBDATA_DIR)
        os.makedirs(web_contents_dir, exist_ok=True)

        for url, text in extracted_texts.items():
            filename = generate_filename_from_url(url)
            filepath = os.path.join(web_contents_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
        return True
    else:
        return False


def extract_contents_for(urls):
    """
    Extracts text from URLs and saves them to a file.
    """

    extracted_texts = extract_texts_from_multiple_webpages(urls)
    if extracted_texts and save_extracted_texts(extracted_texts):
        return True
    return False
