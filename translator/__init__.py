# ToDO: Implement a better script to detect country of origin of user requests,
# Use ip and langdetect to detect language of origin of requests
########################################################################################################

import json
import logging
from typing import List, Tuple, Union

from langdetect import DetectorFactory, detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException

from config.settings import LANGUAGES_PATH, LOG_DIR, setup_logger

# setup logging
setup_logger(LOG_DIR)

# Setting the seed to ensure consistent results
DetectorFactory.seed = 0

ENGLISH = "en"


def detect_language(text: str) -> Tuple[str, Union[List[str], str]]:
    try:
        # Detect the most probable language
        language = detect(text)

        # Detect languages with probabilities
        languages_with_probabilities = [str(lang) for lang in detect_langs(text)]
        logging.info(
            f"detecting language: {language} with probabilities: {languages_with_probabilities}"
        )
        return language, languages_with_probabilities
    except LangDetectException as e:
        logging.error(f"detecting language: {language}")
        return "error", str(e)


def load_files():
    languages = None

    if languages is None:
        with open(LANGUAGES_PATH, "r", encoding="utf-8") as file:
            languages = json.load(file)
        return languages
    return languages


def get_language_name(text: str) -> str:

    lang_abbr = detect_language(text)[0]

    files = load_files()
    return files.get(lang_abbr)


def is_english(text: str) -> bool:
    return detect_language(text)[0] == ENGLISH


def to_english(text: str, lang: str = ENGLISH) -> str:
    pass


def from_english(text: str, lang: str = ENGLISH) -> str:
    pass
