# Project Requirement Document 1
Date: 2024-10-07

## 1. Introduction
### 1.1 Purpose
The `VectorVault` is a quick and dirty upload client for vector database(s). 

### 1.2 Initial Scope
The `VectorVault` will contain the following methods in the `src` directory:
- `load` - Loads a document from a local directory and return a langchain `Document` object. Must be able to handle file of different types. Prioritize PDFs to start with.
- `chunk` - Chunks a document into smaller chunks
- `upload` - Uploads chunks to a vector database as an embedding.

These methods are general functions of the application and can be split into sub-methods. Although simplicity is a priority or this initial version.

### 1.3 Local Vault
There is a direcotry `_local_vault` in the root directory that will store all the data locally. The application should be able to find the contents of this directory during loading, run them through all the methods, and then upload the results to the vector database. 

State management is a crucial part of this application. I do not want to upload the same document twice. Once a document is uploaded the program must locally produce metadata or move the file to a different directory so that is obvious that it is uploaded.

### 1.4 Vector Database
This program uses pinecone as the vector database.

### 1.5 Embeddings
This program uses openai embeddings.

### 1.6 Langchain
This program uses langchain to manage the documents and the chunks.

### 1.7 Authentication
Don't worry the keys are in the environment variables and don't need to be directly inputted into the code.

## 2. System Design
### 2.1 Directory Structure

```
vectorvault/
├── _local_vault/
│   ├── unprocessed/
│   │   ├── file3.pdf
│   │   ├── file4.pdf
│   │   └── ...
│   ├── processed/
│   │   ├── file1.pdf
│   │   ├── file2.pdf
│   │   └── ...
├── src/
│   ├── utils.py
├── main.py
```

### 2.2 File Descriptions
- `main.py` - The main application that runs the program.
- `utils.py` - Utility functions for the application.

### 2.3 State Management
- `_local_vault/unprocessed/` - The directory that contains all the files that are not uploaded to the vector database.
- `_local_vault/processed/` - The directory that contains all the files that are uploaded to the vector database.

A method must exist to move a file from `_local_vault/unprocessed/` to `_local_vault/processed/`. Try to do this efficiently as some files may be large.

## 3. Code Examples
Here are some examples to borrow from as you develop. 

### 3.1 End to End Python Rag
This example contains upload and retrieval.
```python
# %% [markdown]
# # Meta Rag with Pinecone
# (20240926) Making the meta rag example work with Pinecone
# 

# %%
import os
import getpass
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import time


# %%
## Initialize Pinecone

pc = Pinecone()

index_name = "langchain-test-index"
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI embeddings dimension
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)


# %%
## Document Loading and Splitting

pdf_loader = PyPDFLoader("documents/building_llm_applications_book.pdf")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
embeddings_model = OpenAIEmbeddings()

# Load and split the PDF
pdf_documents = pdf_loader.load()
pdf_chunks = text_splitter.split_documents(pdf_documents)

print(f"Number of chunks: {len(pdf_chunks)}")

if pdf_chunks:
    first_chunk = pdf_chunks[0]
    print(f"Content of the first chunk: {first_chunk.page_content[:100]}...")
    print(f"Metadata of the first chunk: {first_chunk.metadata}")

# %%
## Initialize Pinecone Vector Store
vector_store = PineconeVectorStore(index=index, embedding=embeddings_model)

# Add documents to the vector store
vector_store.add_documents(pdf_chunks)


# %%
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.schema import StrOutputParser

string_output_parser = StrOutputParser()


import json

def create_debug_wrapper(name=""):
    def debug_wrapper(x):
        print(f"\n--- Debug: {name} Input ---")
        print(json.dumps(x, indent=2, default=str))
        return x  # Just pass through the input
    return RunnableLambda(debug_wrapper)

rag_prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
{context}
Question: {question}
Helpful Answer:"""

rag_prompt = PromptTemplate.from_template(rag_prompt_template)
retriever = vector_store.as_retriever()

chatbot = ChatOpenAI(model_name="gpt-4o-mini")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    }
    | create_debug_wrapper("Context and Question")
    | rag_prompt 
    | create_debug_wrapper("Formatted Prompt")
    | chatbot 
    | create_debug_wrapper("ChatBot Response")
    | string_output_parser
)

def execute_chain(chain, question):
    print("\n=== Starting RAG Chain Execution ===\n")
    answer = chain.invoke(question)
    print("\n=== RAG Chain Execution Complete ===\n")
    return answer

# %%
answer = rag_chain.invoke("tell me about tokens")
```

### 3.2 Multi File Type Upload
This example contains uploading files of different types.
```python
# %% [markdown]
# # Q&A across documents with LangChain and LangSmith

# %%
from langchain_community.document_loaders import WikipediaLoader, Docx2txtLoader, PyPDFLoader, TextLoader

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# %%
import getpass
OPENAI_API_KEY = getpass.getpass('Enter your OPENAI_API_KEY')

# %% [markdown]
# ## Setting up vector database and embeddings

# %%
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vector_db = Chroma("tourist_info", embeddings_model)

# %%
wikipedia_loader = WikipediaLoader(query="Paestum")
wikipedia_chunks = text_splitter.split_documents(wikipedia_loader.load())
vector_db.add_documents(wikipedia_chunks)

# %%
word_loader = Docx2txtLoader("Paestum/Paestum-Britannica.docx")
word_chunks = text_splitter.split_documents(word_loader.load())
vector_db.add_documents(word_chunks)

# %%
pdf_loader = PyPDFLoader("Paestum/PaestumRevisited.pdf")
pdf_chunks = text_splitter.split_documents(pdf_loader.load())
vector_db.add_documents(pdf_chunks)

# %%
txt_loader = TextLoader("Paestum/Paestum-Encyclopedia.txt")
txt_chunks = text_splitter.split_documents(txt_loader.load())
vector_db.add_documents(txt_chunks)

# %% [markdown]
# ### Removing duplication

# %%
def split_and_import(loader):
     chunks = text_splitter.split_documents(loader.load())
     vector_db.add_documents(chunks)
     print(f"Ingested chunks created by {loader}")

# %%
wikipedia_loader = WikipediaLoader(query="Paestum")
split_and_import(wikipedia_loader)

word_loader = Docx2txtLoader("Paestum/Paestum-Britannica.docx")
split_and_import(word_loader)

pdf_loader = PyPDFLoader("Paestum/PaestumRevisited.pdf")
split_and_import(pdf_loader)

txt_loader = TextLoader("Paestum/Paestum-Encyclopedia.txt")
split_and_import(txt_loader)

# %% [markdown]
# ## Ingesting Multiple Documents from a Folder (two techniques)

# %% [markdown]
# ### 1) Iterating over all files in a folder

# %%
loader_classes = {
    'docx': Docx2txtLoader,
    'pdf': PyPDFLoader,
    'txt': TextLoader
}

# %%
import os

def get_loader(filename):
    _, file_extension = os.path.splitext(filename) #A Extract the file extension
    file_extension = file_extension.lstrip('.') #B Remove the leading dot from the extension
    
    loader_class = loader_classes.get(file_extension) #C Get the loader class from the dictionary
    
    if loader_class:
        return loader_class(filename) #D Instantiate and return the correct loader
    else:
        raise ValueError(f"No loader available for file extension '{file_extension}'")

# %% [markdown]
# #### Ingesting the files from the folder (Exercise solution)

# %%
folder_path = "CilentoTouristInfo" #A Path to the folder containing the documents

for filename in os.listdir(folder_path): #B iterate over the files in the path
    file_path = os.path.join(folder_path, filename) #C Construct the full path to the file
   
    if os.path.isfile(file_path): #D Check if it is a file (not a directory)
        try:
            loader = get_loader(file_path) #E Instantiate the correct loader for the file
            print(f"Loader for {filename}: {loader}")
            split_and_import(loader) #F Split and ingest
        except ValueError as e:
            print(e)

# %% [markdown]
# ### 2) Ingesting all files with with DirectoryLoader

# %%
# ONLY RUN THIS IF YOU HAVE SUCCESFULLY INSTALLED unstructured or langchain-unstructured
# THE INSTALLATION IS OPERATIVE SYSTEM SPECIFIC
# follow LangChain instructions at https://python.langchain.com/v0.2/docs/integrations/providers/unstructured/ or 
# Unstructured instructions at https://docs.unstructured.io/welcome#quickstart-unstructured-open-source-library
folder_path = "CilentoTouristInfo"
pattern = "**/*.{docx,pdf,txt}" #A Pattern to match .docx, .pdf, and .txt files

directory_loader = DirectoryLoader(folder_path, pattern) #B Initialize the DirectoryLoader with the folder path and pattern
split_and_import(directory_loader)

# %% [markdown]
# ## Querying the vector store directly

# %%
query = "Where was Poseidonia and who renamed it to Paestum" 
results = vector_db.similarity_search(query, 4) # four clostest results
print(results)

# %%
len(results)

# %% [markdown]
# ## Asking a question through a RAG chain

# %%
from openai import OpenAI
import getpass

OPENAI_API_KEY = getpass.getpass('Enter your OPENAI_API_KEY')

# %%
from langchain_core.prompts import PromptTemplate

rag_prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
{context}
Question: {question}
Helpful Answer:"""

rag_prompt = PromptTemplate.from_template(rag_prompt_template)

# %%
retriever = vector_db.as_retriever()

# %%
from langchain_core.runnables import RunnablePassthrough
question_feeder = RunnablePassthrough()

# %%
from langchain_openai import ChatOpenAI

chatbot = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-4o-mini")

# %%
# set up RAG chain

rag_chain = {"context": retriever, "question": question_feeder} | rag_prompt | chatbot

# %%
def execute_chain(chain, question):
    answer = chain.invoke(question)
    return answer

# %%
question = "Where was Poseidonia and who renamed it to Paestum. Also tell me the source." 
answer = execute_chain(rag_chain, question)
print(answer.content)

# %%
print(answer)

# %%
question = "And then, what did they do?" 
answer = execute_chain(rag_chain, question)
print(answer.content)

# %% [markdown]
# ## Chatbot memory of message history

# %%
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableLambda

rag_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant, world-class expert in Roman and Greek history, especially in towns located in southern Italy. Provide interesting insights on local history and recommend places to visit with knowledgeable and engaging answers. Answer all questions to the best of your ability, but only use what has been provided in the context. If you don't know, just say you don't know. Use three sentences maximum and keep the answer as concise as possible."),
        ("placeholder", "{chat_history_messages}"),
        ("assistant", "{retrieved_context}"),
        ("human", "{question}"),
    ]
)

retriever = vector_db.as_retriever()
question_feeder = RunnablePassthrough()
chatbot = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-4o-mini")
chat_history_memory = ChatMessageHistory()

def get_messages(x):
    return chat_history_memory.messages

rag_chain = {
    "retrieved_context": retriever, 
    "question": question_feeder,
    "chat_history_messages": RunnableLambda(get_messages)
} | rag_prompt | chatbot

def execute_chain_with_memory(chain, question):
    chat_history_memory.add_user_message(question)
    answer = chain.invoke(question)
    chat_history_memory.add_ai_message(answer)
    print(f'Full chat message history: {chat_history_memory.messages}\n\n')                                      
    return answer

# %%
question = "Where was Poseidonia and who renamed it to Paestum? Also tell me the source." 
answer = execute_chain_with_memory(rag_chain, question)
print(answer.content)

# %%
question = "And then what did they do? Also tell me the source" 
answer = execute_chain_with_memory(rag_chain, question)
print(answer.content)

# %% [markdown]
# ## Tracing with LangSmith

# %%
from langsmith import trace
from langsmith import Client, traceable

# %%
LANGSMITH_API_KEY= getpass.getpass('Enter your LANGSMITH_API_KEY')

# %%
langsmith_client = Client(
    api_key=LANGSMITH_API_KEY,
    api_url="https://api.smith.langchain.com",  
)

# %%
question = "Where was Poseidonia and who renamed it to Paestum. Also tell me the source." 
with trace("Chat Pipeline", "chain", project_name="Q&A chatbot", inputs={"input": question}, client=langsmith_client) as rt:
    answer = execute_chain(rag_chain, question)
    print(answer)
    rt.end(outputs={"output": answer})

# %% [markdown]
# ## Setting up Q&A chain with RetrievalQA

# %%
from langchain.chains import RetrievalQA
rag_chain = RetrievalQA.from_chain_type(llm=chatbot, chain_type="stuff", retriever=retriever, return_source_documents=False)

# %%
question = "Where was Poseidonia and who renamed it to Paestum. Also tell me the source." 
with trace("RetrievalQA", "chain", project_name="Q&A chatbot", inputs={"input": question}, client=langsmith_client) as rt:
    answer = execute_chain(rag_chain, question)
    print(answer)
    rt.end(outputs={"output": answer})


```