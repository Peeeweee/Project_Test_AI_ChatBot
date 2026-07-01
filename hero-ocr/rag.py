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

class GenerationCancelled(Exception):
    """Raised when the user cancels an in-flight generation."""
    pass

def ask_hero(question: str, cancel_event=None) -> str:
    """
    Queries the vectorstore using Ollama (mistral) to answer the user's question
    based on the loaded documents. Supports cancellation via cancel_event.
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
        "You are HeRO, which stands for Human Resource Officer. You are the official AI assistant of DTI Region 11's Human Resource Department. Your sole purpose is to answer questions based strictly on DTI's official policies, memorandums, HR guidelines, and internal documents that have been provided to you.\n\n"
        "Always be professional, respectful, and concise in your responses. If a question is outside the scope of your knowledge base or cannot be answered from the documents provided, politely say that you do not have information on that topic and suggest that the employee contact the HR Department directly for assistance.\n\n"
        "Never make up information. Never answer from general knowledge. Only answer from the documents you have been given.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
    
    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # 6. Stream the chain and check for cancellation between chunks
    try:
        collected = []
        for chunk in qa_chain.stream(question):
            if cancel_event and cancel_event.is_set():
                raise GenerationCancelled()
            collected.append(chunk)
        return "".join(collected)
    except GenerationCancelled:
        partial = "".join(collected)
        if partial.strip():
            return partial.strip() + "\n\n⚠️ *Generation was cancelled.*"
        return "⚠️ Generation was cancelled by the user."

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
