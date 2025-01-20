import os
import shutil
import logging
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

from src.html_loader import CustomHTMLLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directories
UNPROCESSED_DIR = os.path.join("_local_vault", "unprocessed")
PROCESSED_DIR = os.path.join("_local_vault", "processed")

if not os.path.exists(UNPROCESSED_DIR):
    os.makedirs(UNPROCESSED_DIR)
if not os.path.exists(PROCESSED_DIR):
    os.makedirs(PROCESSED_DIR)

def load_file(file_path: str) -> List[Document]:
    """
    Loads a document from the given file path and returns a list of LangChain Document objects.
    """
    try:
        # Determine the file type and use the appropriate loader
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path)
        elif file_path.endswith('.html'):
            loader = CustomHTMLLoader(file_path)
        else:
            logging.warning(f"Unsupported file type for {file_path}")
            return []

        documents = loader.load()
        # Attach metadata
        for doc in documents:
            doc.metadata['file_name'] = os.path.basename(file_path)
        logging.info(f"Loaded document from {file_path}")
        return documents

    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return []

def chunk_document(documents: List[Document]) -> List[Document]:
    """
    Splits Documents into smaller chunks suitable for embedding and uploading to the vector database.
    """
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=250)
        chunks = text_splitter.split_documents(documents)
        
        # Add a unique chunk_id to each chunk's metadata
        for idx, chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = idx
        
        logging.info(f"Documents split into {len(chunks)} chunks")
        return chunks

    except Exception as e:
        logging.error(f"Error chunking documents: {e}")
        return []

def upload_chunks(chunks: List[Document], vector_store: PineconeVectorStore):
    """
    Uploads the list of document chunks to the vector database (Pinecone).
    """
    try:
        vector_store.add_documents(chunks)
        logging.info(f"Uploaded {len(chunks)} chunks to the vector database")

    except Exception as e:
        logging.error(f"Error uploading chunks: {e}")

def move_file_to_processed(file_path: str):
    """
    Moves a file from the unprocessed directory to the processed directory,
    preserving the directory structure.
    """
    try:
        # Calculate the relative path from the unprocessed directory
        relative_path = os.path.relpath(file_path, UNPROCESSED_DIR)
        dest_path = os.path.join(PROCESSED_DIR, relative_path)

        # Create the destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Move the file
        shutil.move(file_path, dest_path)
        logging.info(f"Moved {file_path} to {dest_path}")

    except Exception as e:
        logging.error(f"Error moving file {file_path} to processed: {e}")

def is_file_processed(file_name: str) -> bool:
    """
    Checks if a file has already been processed and uploaded.
    """
    processed_file_path = os.path.join(PROCESSED_DIR, file_name)
    exists = os.path.exists(processed_file_path)
    logging.debug(f"File {file_name} processed: {exists}")
    return exists

def get_unprocessed_files() -> List[str]:
    """
    Retrieves a list of file paths from the unprocessed directory, including subdirectories.
    """
    try:
        files = []
        for root, dirs, filenames in os.walk(UNPROCESSED_DIR):
            for filename in filenames:
                if not filename.startswith('.'):  # skip hidden files
                    file_path = os.path.join(root, filename)
                    files.append(file_path)
        logging.info(f"Found {len(files)} unprocessed files")
        return files

    except Exception as e:
        logging.error(f"Error retrieving unprocessed files: {e}")
        return []

def process_file(file_path: str, vector_store: PineconeVectorStore):
    """
    Orchestrates the processing of a single file: loading, chunking, uploading, and moving.
    """
    try:
        file_name = os.path.basename(file_path)
        if is_file_processed(file_name):
            logging.info(f"File {file_name} has already been processed.")
            return

        documents = load_file(file_path)
        if not documents:
            logging.warning(f"Skipping file {file_name}")
            return

        chunks = chunk_document(documents)
        if not chunks:
            logging.warning(f"No chunks created for {file_name}")
            return

        upload_chunks(chunks, vector_store)
        move_file_to_processed(file_path)
        logging.info(f"Successfully processed {file_name}")

    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")

def process_all_unprocessed_files(vector_store: PineconeVectorStore):
    """
    Processes all unprocessed files in the unprocessed directory.
    """
    files = get_unprocessed_files()
    for file_path in files:
        process_file(file_path, vector_store)