import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from PyPDF2 import PdfReader

from config.settings import LOG_DIR, PDFDATA_DIR, setup_logger

setup_logger(LOG_DIR)


def extract_text_from_pdf(pdf_path: str, output_directory: str) -> Optional[str]:
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            logging.info(f"Processing '{pdf_path}', Total Pages: {total_pages}")

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            txt_filename = (
                os.path.splitext(os.path.basename(pdf_path))[0].lower() + ".txt"
            )
            txt_path = os.path.join(output_directory, txt_filename)

            with open(txt_path, "w", encoding="utf-8") as text_file:
                text = text.lower()
                text_file.write(text)

            return txt_path
    except Exception as e:
        logging.error(f"Error processing '{pdf_path}': {e}")
        return None


def extract_text_from_pdfs_in_directory(directory: str) -> None:
    # Ensure the output directory exists
    os.makedirs(PDFDATA_DIR, exist_ok=True)

    pdf_files = [
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.endswith(".pdf")
    ]

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(extract_text_from_pdf, pdf_path, PDFDATA_DIR)
            for pdf_path in pdf_files
        ]

        for future in as_completed(futures):
            result = future.result()
            if result:
                logging.info(f"Successfully processed '{result}'")

    logging.info(
        f"Text extraction complete. Extracted texts are saved in '{PDFDATA_DIR}'."
    )
