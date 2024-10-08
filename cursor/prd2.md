# Project Requirement Document 2
Date: 2024-10-07

## 1. Design Specifics
The 2nd version of the project requirement document will focus on the design specifics of the application. Files, objects, and methods will be laid out here in English or code snippets. The entire flow of the application will be understood in detail. From this document, a junior developer should be able to implement the application.

## 2. utils.py

`utils.py` will contain the following utility functions:

### 2.1 `load_file(file_path: str) -> Document`
- **Description**: Loads a document from the given file path and returns a LangChain `Document` object.
- **Supported File Types**: Initially prioritize PDFs, but design the function to be easily extendable to support other file types (e.g., DOCX, TXT).
- **Implementation Details**:
  - Use appropriate document loaders from LangChain or custom loaders for different file types.
  - Handle exceptions for unsupported file types and log warnings.
  - Extract and attach metadata (e.g., file name, creation date) to the `Document` object.

### 2.2 `chunk_document(document: Document) -> List[Document]`
- **Description**: Splits a `Document` into smaller chunks suitable for embedding and uploading to the vector database.
- **Implementation Details**:
  - Utilize LangChain's `RecursiveCharacterTextSplitter` or similar splitter.
  - Configure chunk size (e.g., 500 characters) and overlap (e.g., 50 characters) for optimal performance.
  - Ensure that chunks do not split sentences or important semantic units.

### 2.3 `upload_chunks(chunks: List[Document])`
- **Description**: Uploads the list of document chunks to the vector database (Pinecone).
- **Implementation Details**:
  - Use OpenAI embeddings to convert text chunks into vector embeddings.
  - Interact with Pinecone's API to upload vectors.
  - Handle API rate limits and errors gracefully.
  - Log successful uploads and any issues encountered.

### 2.4 `move_file_to_processed(file_path: str)`
- **Description**: Moves a file from `_local_vault/unprocessed/` to `_local_vault/processed/` to signify that it has been uploaded.
- **Implementation Details**:
  - Use efficient file operations to move large files without unnecessary copying.
  - Handle potential file name conflicts in the `processed` directory.
  - Log the movement of files for auditing purposes.

### 2.5 `is_file_processed(file_name: str) -> bool`
- **Description**: Checks if a file has already been processed and uploaded.
- **Implementation Details**:
  - Check if the file exists in `_local_vault/processed/`.
  - Optionally, maintain a manifest or checksum to track processed files.
  - Use this function to prevent duplicate uploads.

### 2.6 `get_unprocessed_files() -> List[str]`
- **Description**: Retrieves a list of file paths from `_local_vault/unprocessed/` that need to be processed.
- **Implementation Details**:
  - Traverse the `unprocessed` directory and collect file paths.
  - Exclude any hidden or temporary files.
  - Return a sorted list for consistent processing order.

### 2.7 `process_file(file_path: str)`
- **Description**: Orchestrates the processing of a single file: loading, chunking, uploading, and moving.
- **Implementation Details**:
  - Check if the file is already processed using `is_file_processed`.
  - Call `load_file`, `chunk_document`, and `upload_chunks` sequentially.
  - Move the file to the processed directory using `move_file_to_processed`.
  - Include exception handling to ensure robustness.

### 2.8 `process_all_unprocessed_files()`
- **Description**: Processes all unprocessed files in the `_local_vault/unprocessed/` directory.
- **Implementation Details**:
  - Retrieve unprocessed files using `get_unprocessed_files`.
  - Iterate over each file and call `process_file`.
  - Log the overall progress and any files that failed to process.

## 3. Dependencies and Integration
- **Libraries and APIs**:
  - LangChain for document loading and text splitting.
  - OpenAI API for generating embeddings.
  - Pinecone for vector database operations.
  - Standard Python libraries (`os`, `shutil`, `logging`) for file and system operations.
- **Environment Variables**:
  - Ensure OpenAI and Pinecone API keys are accessed securely via environment variables.
- **Logging**:
  - Implement detailed logging for monitoring and debugging.
  - Log levels can be adjusted (DEBUG, INFO, WARNING, ERROR) as needed.

## 4. Error Handling and Edge Cases
- **Unsupported File Types**:
  - Gracefully skip files with unsupported formats and log a warning.
- **API Failures**:
  - Implement retries with exponential backoff for transient API errors.
  - Fail the processing of a file after a certain number of retries and log the error.
- **Large Files**:
  - Monitor memory usage when processing large files.
  - Consider processing large files in chunks if necessary.

## 5. Extensibility Considerations
- Design the utility functions to be modular and reusable.
- Abstract file type handling to easily add support for more formats in the future.
- Allow configuration of chunk sizes and other parameters without changing the code.

## 3. main.py

`main.py` serves as the entry point for the VectorVault application. It orchestrates the overall workflow by utilizing the utility functions defined in `utils.py`.

### 3.1 Responsibilities
- **Initialization**: Sets up logging to track the application's progress and any issues.
- **File Processing**: Manages the retrieval and processing of unprocessed files from the `_local_vault/unprocessed/` directory.
- **Execution Flow**: Calls utility functions to handle the loading, chunking, uploading, and moving of files.

### 3.2 Implementation Details

#### 3.2.1 Logging Configuration
- **Purpose**: To provide detailed logs for monitoring and debugging.
- **Configuration**: Uses Python's `logging` module with a basic configuration that includes timestamps, log levels, and messages.

#### 3.2.2 Main Function
- **Function Name**: `main()`
- **Description**: The core function that runs the application.
- **Steps**:
  1. Logs the start of the application.
  2. Retrieves a list of unprocessed files using `get_unprocessed_files`.
  3. Logs the number of unprocessed files found.
  4. Calls `process_all_unprocessed_files` to process each file.
  5. Logs the completion of the application.

#### 3.2.3 Entry Point
- **Code Block**:
  ```python
  if __name__ == "__main__":
      main()
  ```
- **Purpose**: Ensures that the `main` function is executed when the script is run directly.

### 3.3 Dependencies
- **Modules**: Imports functions from `src.utils` to perform file operations.
- **Environment**: Assumes that the necessary environment variables for API keys are set.

### 3.4 Error Handling
- **Robustness**: Includes logging to capture any errors or issues during execution.
- **Graceful Exit**: Ensures that the application logs any critical failures before exiting.

### 3.5 Extensibility
- **Modular Design**: The main function is designed to be easily extendable to include additional features or processing steps in the future.

