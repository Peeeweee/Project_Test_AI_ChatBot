from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import ask_hero

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
    # FastAPI automatically runs synchronous endpoints in a background threadpool,
    # completely avoiding the async event loop issues we saw with Chainlit!
    answer = ask_hero(request.question)
    return ChatResponse(answer=answer)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Project HeRO API is running."}
