# Chat With Documents – Full-Stack RAG-Powered AI Application
## Overview

Developed an AI-powered web app for my Client that enables users to upload documents (PDFs, TXT, DOC, DOCX, CSV) and interact with them via a smart chat interface. I built the full-stack solution using React, Vite, and FastAPI, with OpenAI’s API and FAISS for semantic search. Integrated secure file uploads, and a Retrieval-Augmented Generation (RAG) pipeline for accurate, context-aware responses. Delivered a scalable, intuitive solution that simplifies document comprehension and enhances productivity.

## Features
- 📁 Upload PDF, DOCX, DOC and CSV.
- 💬 Chat interface to ask questions about uploaded documents
- 🧠 RAG-based pipeline with LlamaIndex + FAISS
- 🌐 React frontend + FastAPI backend

## Tech Stack
### Frontend: 
- React + Vite
- Axios for API communication

### Backend:
- FastAPI
- SQLAlchemy + SQLite
- LlamaIndex + FAISS
- OpenAI or HuggingFace Embeddings

## 📦 Installation

### 1. Clone the Repository

```bash```
git clone https://github.com/sameehaasim002/chat-with-doc.git<br />
cd chat-with-doc

### 2. Backend Setup

cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

### 3. Frontend Setup

cd frontend
npm install
npm run dev

### 4. ⚙️ Environment Variables

Create a .env file in the backend/ directory with the following:
OPENAI_API_KEY=your_openai_key

## 📄 Project Structure
chat-with-doc/
├── backend/
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── rag_pipeline/
│   └── ...
├── frontend/
│   ├── src/
│   ├── components/
│   └── ...

## Demo
![Home Page](https://github.com/user-attachments/assets/57f22858-5ffa-48bc-ab94-246f27353cc8)
![Home Page When Sidebar is Open](https://github.com/user-attachments/assets/ebba764f-90d7-4f31-9232-6f722c4ec14e)
![Demo of Chat with Bot](https://github.com/user-attachments/assets/19b310aa-50dc-4853-a9ff-945fc4396952)
![FastAPI Endpoints ](https://github.com/user-attachments/assets/8a310871-6f89-4854-8e40-cf85d6d1e6c3)
![Documents Endpoint Where You Can See Analytics of Files](https://github.com/user-attachments/assets/b11eae70-ef16-4e4c-97df-417cb53805a8)
