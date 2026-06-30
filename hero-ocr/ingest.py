import os
import glob
import json
import re
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

def clean_ocr_text(text: str) -> str:
    """
    Cleans OCR text by fixing common misreads, removing headers/footers, and collapsing whitespace.
    """
    # 1. Remove repeating headers/footers
    text = re.sub(r'^\s*ANNEX\s+[A-Z]\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'^\s*List of BuB FY 2015 Participating LGUs\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'^\s*Page\s+\d+\s+of\s+\d+\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE) # Standalone page numbers

    # 2. Fix common OCR misreads in ALL CAPS
    replacements = {
        "El,IGIBLE": "ELIGIBLE",
        "ELIG!BLE": "ELIGIBLE",
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)

    # 3. Collapse excessive whitespace from column alignment artifacts
    # Replacing 4+ spaces with a single tab to preserve structure efficiently
    text = re.sub(r' {4,}', '\t', text)

    return text

def is_tabular(block: str) -> bool:
    """
    Heuristics to determine if a block of text is tabular.
    """
    lines = block.strip().split('\n')
    if len(lines) < 3:
        return False
        
    table_lines = 0
    for line in lines:
        if '\t' in line or '   ' in line:
            table_lines += 1
            
    if table_lines / len(lines) > 0.5:
        return True
        
    return False

def process_and_chunk_text(text: str, source: str, text_splitter) -> tuple[list[Document], int, int]:
    """
    Splits text into blocks, categorizes them as prose vs tabular, and chunks accordingly.
    Returns (chunks, prose_count, tabular_count).
    """
    chunks = []
    prose_count = 0
    tabular_count = 0
    
    blocks = re.split(r'\n\s*\n', text)
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        if is_tabular(block):
            # Tabular chunking: group by 10 rows
            lines = block.split('\n')
            batch_size = 10
            for i in range(0, len(lines), batch_size):
                batch_text = '\n'.join(lines[i:i+batch_size])
                chunks.append(Document(page_content=batch_text, metadata={"source": source, "type": "tabular"}))
                tabular_count += 1
        else:
            # Prose chunking
            doc = Document(page_content=block, metadata={"source": source, "type": "prose"})
            prose_chunks = text_splitter.split_documents([doc])
            chunks.extend(prose_chunks)
            prose_count += len(prose_chunks)
            
    return chunks, prose_count, tabular_count

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
    total_prose_chunks = 0
    total_tabular_chunks = 0

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        
        if filename in processed_files:
            print(f"Skipping '{filename}', already ingested.")
            skipped_count += 1
            continue

        print(f"\n--- Starting ingestion for: {filename} ---")
        
        # Extract text using the OCR function from ocr.py
        text = extract_text_from_scanned_pdf(pdf_path)
        
        # Clean the OCR text
        text = clean_ocr_text(text)
        
        if not text.strip():
            print(f"Could not extract any text from {filename}. Skipping.")
            continue
            
        # Process and chunk intelligently
        chunks, prose_count, tabular_count = process_and_chunk_text(text, pdf_path, text_splitter)
        
        print(f"Split text into {len(chunks)} chunks ({prose_count} prose, {tabular_count} tabular). Storing in ChromaDB...")
        
        # Add the chunks to the vectorstore
        vectorstore.add_documents(chunks)
        
        # Mark as processed and save immediately
        processed_files.add(filename)
        save_processed_files(processed_files)
        
        newly_processed_count += 1
        total_prose_chunks += prose_count
        total_tabular_chunks += tabular_count
        
        # Success message after each file is processed
        print(f"Success! '{filename}' has been processed and stored in ChromaDB.")
        
    print("\n--- Ingestion Summary ---")
    print(f"Files skipped (already ingested): {skipped_count}")
    print(f"Files newly processed: {newly_processed_count}")
    print(f"Total prose chunks generated: {total_prose_chunks}")
    print(f"Total tabular chunks generated: {total_tabular_chunks}")
    print("-------------------------")

if __name__ == "__main__":
    main()
