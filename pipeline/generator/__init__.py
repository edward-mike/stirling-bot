import logging
import os

import openai
from dotenv import load_dotenv
from openai import OpenAI

from config.settings import LOG_DIR, setup_logger

setup_logger(LOG_DIR)

load_dotenv()


def generate_question_answer_pairs(*, content: str) -> str:

    openai.api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI()
    # Preprocess the content and generate a list of question,answer pairs
    prompt = f"Generate a list of comma separated questions and their answers based on the following content:\n\n{content}"
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo-1106",
    )
    return completion.choices[0].message.content


def preprocess_files(input_directory: str, output_directory: str) -> None:
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".txt"):
            input_file_path = os.path.join(input_directory, filename)
            with open(input_file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()

            logging.info(f"Generating questions and answers for content in: {filename}")

            generated_text = generate_question_answer_pairs(content=content).lower()
            output_file_path = os.path.join(
                output_directory, os.path.splitext(filename)[0] + ".txt"
            )

            with open(output_file_path, "w") as file:
                file.write(generated_text)

            logging.info(f"Text file created: {output_file_path}")
