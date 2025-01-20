# VectorVault

VectorVault is a quick and efficient upload client for vector databases, designed to handle various document types and upload them as embeddings to a vector database. This project uses Pinecone as the vector database and OpenAI embeddings for vectorization.

## Table of Contents
- [Introduction](#introduction)
- [Setup](#setup)
- [Directory Structure](#directory-structure)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Introduction

VectorVault is designed to streamline the process of uploading documents to a vector database. It supports multiple file types, including PDFs, DOCX, and TXT, and uses LangChain for document management and chunking. The application ensures that documents are not uploaded more than once by maintaining a local state.

## Setup

### Prerequisites

- Python 3.8 or higher
- Pinecone account and API key
- OpenAI account and API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vectorvault.git
   cd vectorvault
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables for your API keys:
   ```bash
   export OPENAI_API_KEY='your-openai-api-key'
   export PINECONE_API_KEY='your-pinecone-api-key'
   ```

## Directory Structure

The project follows this directory structure:

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

- **_local_vault/unprocessed/**: Place your documents here for processing.
- **_local_vault/processed/**: Processed documents are moved here after successful upload.

## Usage

1. **Prepare your documents**: Place the documents you want to upload in the `_local_vault/unprocessed/` directory.

2. **Run the application**: Execute the main script to process and upload your documents.
   ```bash
   python main.py
   ```

3. **Check the logs**: The application logs its progress and any issues encountered. Check the console output for details.

## Dependencies

The project relies on several key libraries and APIs:

- **LangChain**: For document loading and text splitting.
- **OpenAI API**: For generating embeddings.
- **Pinecone**: For vector database operations.
- **Standard Python libraries**: For file and system operations.

Ensure all dependencies are installed via the `requirements.txt` file.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
