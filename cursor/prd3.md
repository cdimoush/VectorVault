# Project Requirement Document 3
## Purpose
I want to add crawling to the upload process. This will allow for tiering of documents inside of the unprocess document directory, The tiers will be used to add complexity to the document metadata. This will be a tiered file structure in the form of metadata strings.

I also want to add chunk id to the chunk uploads so I can trace where chronologically in a document a chunk came from.

## Restated Purpose
The goal is to implement a crawling mechanism within the upload workflow to handle tiered subdirectories under the unprocessed folder. Each tier or subdirectory level will add metadata reflecting where the file was found. Additionally, every chunk uploaded should include a unique chunk ID that indicates its order within the original document. This allows for improved traceability and organization in the document processing pipeline.

## Steps for Implementation

1. Tiered Subdirectory Crawling
   - Update the file retrieval system (see README.md for current directory structure) to recursively find files in subfolders under "_local_vault/unprocessed/".  
   - Each subfolder (tier) will be noted in the file's metadata so that we can track and manage documents based on their tier.

2. Tier Metadata Addition
   - When a file is loaded in utils.py, store the subdirectory path or "tier" in a metadata field.  
   - Consider using structure like "doc.metadata['tiers'] = [list_of_subdirectories]" for clarity.

3. Unique Chunk IDs
   - Modify or extend the chunking process in utils.py to assign a "chunk_id" to each piece of text.  
   - This ID could be a simple incremental counter or generated using the combination of filename + chunk index.  
   - Store it in doc.metadata['chunk_id'] (or a similar field) before uploading to the vector database.

4. Integration & Verification
   - Ensure that each chunk (with the new metadata) is successfully uploaded to the Pinecone vector store.  
   - Verify by checking the console logs and Pinecone records that the tiers and chunk IDs appear as expected.

5. Documentation & Updates
   - Update the README.md usage instructions to mention support for subdirectories under "_local_vault/unprocessed/".  
   - Provide clear examples or best practices for how to name or organize tiers.  
   - After confirming functionality, finalize and document the full process so future changes are straightforward.

## Handling Tiered Directories in get_unprocessed_files

To accommodate tiered subdirectories under "_local_vault/unprocessed/", the get_unprocessed_files function can be updated to use Python's os.walk() to recursively traverse the directory structure. Though the function can still return a flat list of file paths, it should ensure that all subfolders are visited.

Below is a conceptual approach:

- Use os.walk(UNPROCESSED_DIR) instead of os.listdir(UNPROCESSED_DIR).  
- For each level of the directory tree (root, subdirs, files), collect the file paths into a list.  
- Skip hidden files or directories starting with ".".  

Example in pseudo-code:

```python
def get_unprocessed_files() -> List[str]:
    files = []
    for root, dirs, filenames in os.walk(UNPROCESSED_DIR):
        for filename in filenames:
            if not filename.startswith('.'):  # skip hidden files
                file_path = os.path.join(root, filename)
                files.append(file_path)
    return files
```

This modification would allow all files under the unprocessed folder (including those in deeper subdirectories) to be returned in a single list, which then can be processed normally in the rest of the pipeline. The subdirectory information (for tiers) can later be extracted from the file path itself and added to the metadata, if needed.
