# 🤖 Test AI ChatBot

<div align="center">
  <img alt="React" src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" />
  <img alt="Ollama" src="https://img.shields.io/badge/Ollama-FFFFFF?style=for-the-badge&logo=Ollama&logoColor=black" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
</div>

<br />

**Test AI ChatBot** is a fully local, completely private OCR-powered Retrieval-Augmented Generation (RAG) assistant. It extracts text from your scanned PDFs, chunks and vectorizes the data into ChromaDB, and provides a stunning React-based dark-mode chat interface to interact with your documents using a local LLM (Mistral via Ollama).

---

## ✨ Features

- **100% Local & Private**: No API keys required. Your documents never leave your machine.
- **Smart OCR Pipeline**: Automatically converts scanned PDFs to images and extracts text using Tesseract.
- **Modern Architecture**: Decoupled React frontend (Vite) and FastAPI backend.
- **Beautiful UI**: Sleek, pitch-black glassmorphism design with Montserrat typography.
- **Incremental Ingestion**: Smart processing only vectorizes *new* documents, skipping already ingested files.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your system:
- **[Python 3.13+](https://www.python.org/downloads/)** (Ensure this is in your global PATH)
- **[Node.js](https://nodejs.org/)**: Required to run the React frontend.
- **[Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)**: Needs to be installed and accessible in your system's PATH.
- **[Ollama](https://ollama.com/)**: Needs to be installed and running in the background.
  - *Don't forget to pull the model: `ollama pull mistral`*

---

## 🚀 Getting Started

### 1. Install Backend Dependencies
Open a terminal in the root `hero-ocr` directory:
```bash
python -m pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
Navigate to the frontend folder and install Node packages:
```bash
cd frontend
npm install
```

---

## 📚 Adding Knowledge (PDFs)

1. Drop your scanned PDF documents directly into the `documents/` folder.
2. Open a terminal in the `hero-ocr` directory and extract the text to your local vector database:
```bash
python ingest.py
```
*(You can run this anytime you add new PDFs. It will automatically skip documents that have already been ingested!)*

---

## 💻 Running the App

Because the app uses a decoupled architecture, you will need to start the backend API and the frontend UI in **two separate terminals**.

### Terminal 1: Start the Backend API (FastAPI)
Open a terminal in the `hero-ocr` directory and run:
```bash
python -m uvicorn server:app --reload
```
*(If you have Python version issues on Windows, use the full path to your stable python: `C:\Python313\python.exe -m uvicorn server:app --reload`)*

### Terminal 2: Start the Frontend UI (React)
Open a **new, separate terminal**, navigate to the frontend folder, and run:
```bash
cd frontend
npm run dev
```
Click the local web address (usually `http://localhost:5173`) that appears in the terminal to view your chat interface in the browser!

---

## 🐛 Troubleshooting

| Error | Cause & Fix |
|-------|-------------|
| **`TesseractNotFoundError`** | Python cannot find the Tesseract executable. Ensure Tesseract is installed and added to your system's Environment Variables (PATH). |
| **Failed to connect to Ollama** | The Ollama service is not running. Launch the Ollama application from your start menu, then restart the app. |
| **`ModelNotFoundError`** | You haven't downloaded the Mistral model yet. Run `ollama pull mistral` in your terminal. |
| **`ModuleNotFoundError` (fastapi)** | You might be mixing incompatible Python virtual environments. Run the server using your stable Python installation explicitly: `C:\Python313\python.exe -m uvicorn server:app --reload`. |
