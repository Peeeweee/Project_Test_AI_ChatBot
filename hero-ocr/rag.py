from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def ask_hero(question: str) -> str:
    """
    Queries the vectorstore using Ollama (mistral) to answer the user's question
    based on the loaded documents.
    """
    # 1. Initialize Ollama embeddings with the mistral model
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # 2. Load the existing ChromaDB vectorstore
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings
    )
    
    # 3. Create a retriever from the vectorstore
    retriever = vectorstore.as_retriever()
    
    # 4. Initialize Ollama with mistral model as the LLM
    llm = Ollama(model="mistral")
    
    # 5. Build the QA chain using modern LCEL
    prompt = PromptTemplate.from_template(
        "You are Project HeRO, an HR Assistant. Answer the question based only on the following context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )
    
    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # 6. Run the chain with the input question
    response = qa_chain.invoke(question)
    
    # 7. Return the answer string
    return response

def get_knowledge_base():
    """
    Retrieves all documents stored in the ChromaDB vectorstore,
    groups them by source filename, and returns the structured data.
    """
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings
    )
    
    collection = vectorstore._collection
    results = collection.get()
    
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    
    grouped_data = {}
    for doc, meta in zip(documents, metadatas):
        source_path = meta.get("source", "Unknown")
        source_filename = os.path.basename(source_path)
        
        if source_filename not in grouped_data:
            grouped_data[source_filename] = []
            
        grouped_data[source_filename].append(doc)
        
    return grouped_data
