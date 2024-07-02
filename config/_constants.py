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
