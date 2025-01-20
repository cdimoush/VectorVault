import sys
import os

# Add the directory containing 'src' to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.html_loader import CustomHTMLLoader
from langchain_community.document_loaders import BSHTMLLoader

def main():
    # Specify the path to the HTML file
    file_path = "_dev/tutorial_core_hello_world.html"
    
    # Create an instance of the CustomHTMLLoader
    loader = BSHTMLLoader(file_path)
    # loader = CustomHTMLLoader(file_path)
    
    # Load the content of the <main> tag with id="main-content"
    elements_with_ids = {"main": "main-content"}
    # documents = loader.load(elements_with_ids=elements_with_ids)
    documents = loader.load()
    
    # Print the loaded content
    for document in documents:
        print("Title:", document.metadata.get("title", "No Title"))
        print("Content:", document.page_content)

if __name__ == "__main__":
    main() 