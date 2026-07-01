# Frontend UI

This folder contains the React frontend for the Project HeRO project. 

## How to Run the Frontend

If you are just looking to run the user interface, follow these steps:

### 1. Install Dependencies
Open a terminal in this `frontend` folder and run:
```bash
npm install
```

### 2. Start the Development Server
Once dependencies are installed, start the local server:
```bash
npm run dev
```

### How to Run BackEnd?
C:\Python313\python.exe -m uvicorn server:app --reload

### How to Run FrontEnd?
cd frontend
npm run dev

This will output a local address (usually `http://localhost:5173`). Click it or paste it into your browser to view the chat interface!

*(Note: The chat interface requires the FastAPI backend to be running simultaneously to actually answer questions. See the [Main README](../README.md) in the root directory for instructions on starting the backend API.)*
