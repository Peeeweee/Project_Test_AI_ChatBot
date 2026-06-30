import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")

def inspect():
    print("Loading vectorstore from:", VECTORSTORE_DIR)
    
    # Initialize embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Load vectorstore
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings
    )
    
    # Get all documents directly from the underlying Chroma collection
    collection = vectorstore._collection
    results = collection.get()
    
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    
    unique_sources = set()
    total_chunks = len(documents)
    
    print("\n--- CHUNK INSPECTION ---\n")
    for i, (doc, meta) in enumerate(zip(documents, metadatas)):
        # Extract just the filename from the absolute path to keep it clean
        source_path = meta.get("source", "Unknown")
        source_filename = os.path.basename(source_path)
        unique_sources.add(source_filename)
        
        print(f"[{i+1}/{total_chunks}] Source: {source_filename}")
        print("-" * 60)
        print(doc.strip())
        print("-" * 60)
        print("\n")
        
    print("=== KNOWLEDGE SUMMARY ===")
    print(f"Total Chunks Stored: {total_chunks}")
    print(f"Unique Sources Found: {len(unique_sources)}")
    print("Documents in Database:")
    for src in sorted(unique_sources):
        print(f" - {src}")

if __name__ == "__main__":
    inspect()
