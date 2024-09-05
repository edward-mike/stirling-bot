import logging
import os
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from configparser import ConfigParser
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import streamlit as st
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Pinecone as lgPinecone
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from streamlit_chat import message

from config.settings import (
    CSS_URL,
    DATA_DIR,
    LOG_DIR,
    LOGO_URL,
    BotConfig,
    setup_logger,
)
from new import run_new
from utils import console_text_art, time_execution

warnings.filterwarnings("ignore", category=DeprecationWarning)

config = ConfigParser()
config.read("config.ini")

# setup logging
setup_logger(LOG_DIR)

# extraction and processing
run_new()

# load environment variables
load_dotenv()

########################################################################
# App configuration
########################################################################


@lru_cache
def load_csv_file(file_path: str) -> List[str]:
    try:
        loader = CSVLoader(file_path=file_path)
        return loader.load()
    except (AttributeError, TypeError, RuntimeError) as e:
        logging.error(e)
        return []


@time_execution
def load_csv_data(data_directory: str) -> Tuple[List[str], int]:
    data_list: List[str] = []
    counts: int = 0

    csv_files = [
        os.path.join(data_directory, filename)
        for filename in os.listdir(data_directory)
        if filename.endswith(".csv")
    ]
    counts = len(csv_files)

    with ThreadPoolExecutor() as executor:
        future_to_file = {
            executor.submit(load_csv_file, file_path): file_path
            for file_path in csv_files
        }
        for future in as_completed(future_to_file):
            data_list.extend(future.result())

    return data_list, counts


datasets, counts = load_csv_data(DATA_DIR)


# ########################################################################
# https://python.langchain.com/v0.2/docs/how_to/recursive_text_splitter/

conf = config["DEFAULT"]


@time_execution
def document_splitter(
    documents: List[str],
    chunk_size: int = int(conf["chunk_size"]),
    chunk_overlap: int = int(conf["chunk_overlap"]),
) -> List[List[str]]:
    text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    texts: List[str] = text_splitter.create_documents(
        [doc.page_content for doc in documents]
    )
    return texts


texts = document_splitter(datasets)


def get_openai_embeddings():
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    return embeddings


embeddings = get_openai_embeddings()


index_name = os.environ["INDEX_NAME"]


# @st.cache_resource
@time_execution
def setup_pinecone_index() -> None:

    pc: Pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    spec: ServerlessSpec = ServerlessSpec(
        cloud=os.environ["CLOUD"], region=os.environ["CLOUD_REGION"]
    )

    index_names: Dict[str, Any] = pc.list_indexes().names()
    if index_name not in index_names:
        pc.create_index(
            name=index_name,
            dimension=os.environ["DIMENSIONS"],
            metric=os.environ["METRIC"],
            spec=spec,
        )


setup_pinecone_index()

documents_search = lgPinecone.from_texts(
    [t.page_content for t in texts], embeddings, index_name=index_name
)


llm = OpenAI(
    temperature=os.environ["TEMPERATURE"], openai_api_key=os.environ["OPENAI_API_KEY"]
)
chain = load_qa_chain(llm, chain_type="stuff")


@time_execution
def get_query_response(query: str = None):

    similar_docs = documents_search.similarity_search(
        query, k=int(conf["documents_return_count"])
    )
    response = chain.run(input_documents=similar_docs, question=query)

    return response.strip()


def main() -> None:

    st.set_page_config(
        page_title=f"{BotConfig.name} {BotConfig.page_sub_title}",
        page_icon=BotConfig.emoji,
    )

    # adding custom css to streamlit
    with open(CSS_URL) as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

    st.markdown(
        f'<h1 class="title">{BotConfig.name} <span class="title-bot">B{BotConfig.emoji}t</span></h1>',
        unsafe_allow_html=True,
    )

    if "history" not in st.session_state:
        st.session_state.history = []

    message(BotConfig.welcome_message)

    with st.sidebar:

        st.sidebar.image(LOGO_URL)

        st.sidebar.markdown(
            '<div class="st-emotion-cache-1cypcdb">', unsafe_allow_html=True
        )
        user_input = st.text_input(
            "Your query: ", key="user_input", placeholder="I'm inquiring about..."
        )
        st.sidebar.markdown("</div>", unsafe_allow_html=True)

    if user_input:
        with st.spinner(BotConfig.spinner_message):
            response = get_query_response(user_input)
        st.session_state.history.append({"user": user_input, "bot": response})

    if st.session_state.history:
        for i, chat in enumerate(st.session_state.history):
            message(chat["user"], is_user=True, key=str(i) + "_user")
            message(chat["bot"], key=str(i) + "_bot")


if __name__ == "__main__":
    console_text_art()
    main()
