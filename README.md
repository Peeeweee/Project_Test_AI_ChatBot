# Test AI ChatBot

A full-stack AI chatbot application featuring a React frontend and a FastAPI (Python) backend. It utilizes Ollama for local LLM processing, ChromaDB for vector embeddings, and Tesseract for OCR document ingestion.

## 🛠️ Prerequisites

Ensure you have the following software installed on your machine before starting:

* **Python 3.13**: Matches the project environment (specifically uses `C:\Python313\python.exe`).
* **Node.js**: Required for the React frontend (npm comes with it).
* **Ollama**: Must be installed and running on your machine.
* **Tesseract OCR**: Must be installed separately (not via pip). 
  * *Note: You may need to adjust the Tesseract executable path in `ocr.py` since install paths can differ per machine.*

## 🚀 Installation & Setup

### 1. Pull the Required Ollama Models
Ensure Ollama is running in the background, then pull the required models:
```bash
ollama pull mistral
ollama pull nomic-embed-text

```

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd hero-ocr

```

### 3. Set Up the Python Backend

Create and activate your virtual environment, then install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

```

### 4. Set Up the React Frontend

Open a new terminal or navigate to the frontend directory:

```bash
cd frontend
npm install

```

## 📚 Document Ingestion (Adding Data)

Before chatting, you need to OCR, chunk, and embed your documents into ChromaDB:

1. Place your PDF files into the `documents/` folder.
2. Ensure your virtual environment is active, then run the ingestion script:

```bash
python ingest.py

```

## 💻 Running the Application

### The Recommended Way (All-in-One Launcher)

You can launch both the React frontend and FastAPI backend simultaneously using our convenient start script. Open a terminal in the `hero-ocr` folder and run:

```bash
python start.py
```

This will run both processes in the same terminal and gracefully shut them both down if you press `Ctrl+C`.

### The Manual Way (Two Terminals)

If you prefer to run them separately (e.g., for troubleshooting), you can start them in two different terminals:

### 1. Start the Backend Server

Open a terminal in the root directory, activate your virtual environment, and run:

```bash
C:\Python313\python.exe -m uvicorn server:app --reload

```

*(Note: If your system PATH is configured, you can also just use `python -m uvicorn server:app --reload`)*

### 2. Start the Frontend Server

Open a **separate** terminal, navigate to the frontend folder, and run:

```bash
cd frontend
npm run dev

```

### 3. Open the App

Once both servers are running, open your web browser and visit:
**http://localhost:5173**

You can switch between the two main features using the navigation buttons in the top right of the header:
* **Chat**: The default interface for querying your documents via Ollama.
* **Knowledge Base**: A search-enabled explorer where you can browse through the exact chunks and OCR results stored in ChromaDB, grouped by PDF filename.

*(Note: The chat interface and Knowledge Base view both require the FastAPI backend to be running simultaneously to actually process data.)*

## 🌐 Local Network Access (Other Devices)

This project is configured to be accessible by other devices (like a phone or tablet) connected to the same WiFi network as your laptop. 

1. Ensure the app is running on your laptop using `python start.py`
2. `start.py` will automatically detect your local network IP and update the frontend's `.env` file for you. It will print the detected IP to the console (e.g., `Frontend will be accessible at http://192.168.X.X:5173`).
3. On any other device on the same local network, open a web browser and navigate to the printed URL.

*(Note: Because `start.py` auto-detects the IP, manual `.env` editing is no longer needed for local network testing.)*
