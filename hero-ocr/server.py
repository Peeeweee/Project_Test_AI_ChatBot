import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import ask_hero, get_knowledge_base

# Global cancel event — set it to signal the current generation to stop
cancel_event = threading.Event()

app = FastAPI(title="Test AI ChatBot API")

# Enable CORS for the React frontend (usually running on localhost:5173 for Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Receives a question from the frontend, queries the RAG vectorstore,
    and returns the generated answer.
    """
    # Clear any previous cancel signal before starting
    cancel_event.clear()

    # FastAPI automatically runs synchronous endpoints in a background threadpool,
    # completely avoiding the async event loop issues we saw with Chainlit!
    answer = ask_hero(request.question, cancel_event)
    return ChatResponse(answer=answer)

@app.post("/api/chat/cancel")
def cancel_endpoint():
    """
    Signals the currently running AI generation to stop.
    """
    cancel_event.set()
    return {"status": "cancelled"}

@app.get("/api/knowledge")
def knowledge_endpoint():
    """
    Returns all chunks grouped by their source file.
    """
    return get_knowledge_base()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Project HeRO API is running."}
