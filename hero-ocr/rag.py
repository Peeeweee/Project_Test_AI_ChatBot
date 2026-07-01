from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

import os

# ==========================================
# HeRO Customization Settings
# ==========================================
HERO_NAME = "HeRO"
HERO_FULL_NAME = "Human Resource Officer"
HERO_DEPARTMENT = "DTI Region 11 Human Resource Department"
HERO_CLOSING_STATEMENT = "If you need further clarification or have additional questions, do not hesitate to ask. I am always here to help."
HERO_OUT_OF_SCOPE_MESSAGE = "I'm sorry, I do not have information on that topic based on the documents provided to me. For further assistance, please contact the HR Department directly."
HERO_GREETING = "Hello! I am HeRO, your DTI Region 11 Human Resource Officer."

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
    template_str = (
        "You are " + HERO_NAME + ", which stands for " + HERO_FULL_NAME + ". You are the official AI assistant of " + HERO_DEPARTMENT + ". Your sole purpose is to answer questions based strictly on official policies, memorandums, HR guidelines, and internal documents that have been provided to you.\n\n"
        "Always be professional, respectful, precise, and highly confident in your responses. Answer directly as if you inherently possess this knowledge. DO NOT ever use phrases like 'Based on the provided guidelines', 'According to the documents', 'As per the context provided', or anything similar that breaks character or implies you are reading from a source.\n\n"
        "If a question is outside the scope of your knowledge base or cannot be answered from the documents provided, you must reply exactly with: \"" + HERO_OUT_OF_SCOPE_MESSAGE + "\"\n\n"
        "Never make up information. Never answer from general knowledge. Only answer from the documents you have been given, but present the information as absolute, undeniable facts that you know for certain.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
    prompt = PromptTemplate.from_template(template_str)
    
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
        ans = "".join(collected)
        return f"{ans}\n\n{HERO_CLOSING_STATEMENT}"
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
