import logging
import os
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
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

from config.settings import setup_logger
from config.settings import (DATA_DIR, 
                             LOG_DIR,
                             LOGO_URL, 
                             CHUNK_SIZE,
                             CHUNK_OVERLAP,
                             DOCUMENTS_RETURN_COUNT)
from new import run_new
from utils import time_execution

warnings.filterwarnings("ignore", category=DeprecationWarning)

# setup logging
setup_logger(LOG_DIR)

# extraction and processing
run_new()

# load .env VARIABLES
load_dotenv()

########################################################################
# App configuration
########################################################################


# 1. Load dataset
# @st.cache_data
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
# print(f"files loaded = {counts}")

# ########################################################################
# https://python.langchain.com/v0.2/docs/how_to/recursive_text_splitter/

# 2. Splitting documents
@time_execution
def document_splitter(
    documents: List[str],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[List[str]]:
    text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    # Annotating create_documents method usage
    texts: List[str] = text_splitter.create_documents(
        [doc.page_content for doc in documents]
    )
    return texts

texts = document_splitter(datasets)

# ######################################################################


# # 3. Creating embeddings
def get_openai_embeddings():
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    return embeddings

embeddings = get_openai_embeddings()

# #######################################################################

# Storing embeddings in Pinecone
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

# #######################################################################

# Query Documents using OpenAI - in-Context LLM
llm = OpenAI(
    temperature=os.environ["TEMPERATURE"], openai_api_key=os.environ["OPENAI_API_KEY"]
)
chain = load_qa_chain(llm, chain_type="stuff")

# ######################################################################


# Query
@time_execution
def get_query_response(query: str = None):

    similar_docs = documents_search.similarity_search(query, k=DOCUMENTS_RETURN_COUNT)
    response = chain.run(input_documents=similar_docs, question=query)

    return response.strip()


# StreamLit UI
def main() -> None:
    # Streamlit app
    st.set_page_config(page_title="Stirling FaQ-Bot", page_icon="🤖")

    # Custom CSS
    st.markdown(
        """
        <style>
        
            .title {
                font-size: 3.8rem;
                font-weight: bold;
                color: #433b3b;
                text-align: center;
                margin-top: 20px;
                margin-bottom: 1em;
            }
            
            .title .title-bot {
                color: #88b58a !important;
            }

            /* Style for the sidebar */
            .st-emotion-cache-1cypcdb {
                background-color: #016938 !important;
                margin-bottom: 3em;
            }
            
            .st-emotion-cache-1v0mbdj {
                margin: auto !important;
            }
            
            .st-emotion-cache-1v0mbdj img {
                height: 250px !important;
            }
            
            .st-emotion-cache-l9bjmx p {
                font-size: 16px !important;
                color: #fbf9f9 !important;
            }
            
            .st-emotion-cache-sh2krr p {
                font-size: 16px !important;
            }
            
            .eczjsme4 {
                background-color: #016938 !important;
            }
            
            .eczjsme11 {
                background-color: #016938 !important;
            }
        
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Apply CSS to the title with emoji
    st.markdown(
        '<h1 class="title">Stirling <span class="title-bot">B🤖t</span></h1>',
        unsafe_allow_html=True,
    )

    if "history" not in st.session_state:
        st.session_state.history = []

    message("Hello, how may i help you?")

    with st.sidebar:
        # Logo
        st.sidebar.image(LOGO_URL)
        # Sidebar
        st.sidebar.markdown(
            '<div class="st-emotion-cache-1cypcdb">', unsafe_allow_html=True
        )
        user_input = st.text_input(
            "Your query: ", key="user_input", placeholder="I'm inquiring about..."
        )
        st.sidebar.markdown("</div>", unsafe_allow_html=True)

    if user_input:
        with st.spinner("searching knowledgebase ..."):
            response = get_query_response(user_input)
        st.session_state.history.append({"user": user_input, "bot": response})

    if st.session_state.history:
        for i, chat in enumerate(st.session_state.history):
            message(chat["user"], is_user=True, key=str(i) + "_user")
            message(chat["bot"], key=str(i) + "_bot")


if __name__ == "__main__":
    main()
