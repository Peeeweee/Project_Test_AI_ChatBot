import os
import glob
import json
# pyrefly: ignore [missing-import]
from langchain_text_splitters import RecursiveCharacterTextSplitter
# pyrefly: ignore [missing-import]
from langchain_community.embeddings import OllamaEmbeddings
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import Chroma
# pyrefly: ignore [missing-import]
from langchain_core.documents import Document
from ocr import extract_text_from_scanned_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")
PROCESSED_FILES_LOG = os.path.join(BASE_DIR, "processed_files.json")

def load_processed_files():
    if os.path.exists(PROCESSED_FILES_LOG):
        with open(PROCESSED_FILES_LOG, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_processed_files(processed_files):
    with open(PROCESSED_FILES_LOG, "w", encoding="utf-8") as f:
        json.dump(list(processed_files), f, indent=4)

def main():
    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    # Initialize Ollama embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text") 
    
    # Initialize Chroma vectorstore
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings
    )
    
    # Find all PDFs in the documents folder
    pdf_files = glob.glob(os.path.join(DOCUMENTS_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in the '{DOCUMENTS_DIR}' directory.")
        return

    processed_files = load_processed_files()
    skipped_count = 0
    newly_processed_count = 0

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        
        if filename in processed_files:
            print(f"Skipping '{filename}', already ingested.")
            skipped_count += 1
            continue

        print(f"\n--- Starting ingestion for: {filename} ---")
        
        # Extract text using the OCR function from ocr.py
        text = extract_text_from_scanned_pdf(pdf_path)
        
        if not text.strip():
            print(f"Could not extract any text from {filename}. Skipping.")
            continue
            
        # Create a Langchain Document and split it into chunks
        document = Document(page_content=text, metadata={"source": pdf_path})
        chunks = text_splitter.split_documents([document])
        
        print(f"Split text into {len(chunks)} chunks. Storing in ChromaDB...")
        
        # Add the chunks to the vectorstore
        vectorstore.add_documents(chunks)
        
        # Mark as processed and save immediately
        processed_files.add(filename)
        save_processed_files(processed_files)
        
        newly_processed_count += 1
        
        # Success message after each file is processed
        print(f"Success! '{filename}' has been processed and stored in ChromaDB.")
        
    print("\n--- Ingestion Summary ---")
    print(f"Files skipped (already ingested): {skipped_count}")
    print(f"Files newly processed: {newly_processed_count}")
    print("-------------------------")

if __name__ == "__main__":
    main()
