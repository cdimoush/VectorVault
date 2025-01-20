import logging
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from src.utils import process_all_unprocessed_files
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    pinecone = Pinecone()

    index_name = "langchain-test-index"
    existing_indexes = [index_info["name"] for index_info in pinecone.list_indexes()]

    if index_name not in existing_indexes:
        pinecone.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embeddings dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        while not pinecone.describe_index(index_name).status["ready"]:
            time.sleep(1)

    index = pinecone.Index(index_name)


    index = pinecone.Index(index_name)
    embeddings_model = OpenAIEmbeddings()
    vector_store = PineconeVectorStore(index=index, embedding=embeddings_model)

    # Process all unprocessed files
    process_all_unprocessed_files(vector_store)

if __name__ == "__main__":
    main()