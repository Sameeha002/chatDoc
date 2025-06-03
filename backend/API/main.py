from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from pathlib import Path
import uuid
from datetime import datetime

# Import your RAG system
from testapp import SimpleDocumentRAG  # The optimized class above

app = FastAPI(title="Document Chat API")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

rag_system = SimpleDocumentRAG(
    storage_dir="./storage",
    data_dir=str(UPLOAD_DIR)
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

class DocumentStats(BaseModel):
    total_files: int
    files: List[str]
    last_updated: Optional[str]
    index_size: int

class UploadResponse(BaseModel):
    message: str
    files_processed: int
    files: List[str]

# Global chat sessions (in production, use Redis or database)
chat_sessions = {}

@app.get("/")
async def root():
    return {"message": "Document Chat API is running!"}

@app.post("/upload", response_model=UploadResponse)
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Upload and process documents"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    try:
        # Save uploaded files
        for file in files:
            if not file.filename:
                continue
                
            # Check file type
            allowed_extensions = {'.pdf', '.docx', '.md', '.txt', '.csv'}
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}"
                )
            
            # Save file with unique name to prevent conflicts
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            file_path = UPLOAD_DIR / unique_filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(str(file_path))
        
        # Process documents in background
        def process_documents():
            result = rag_system.add_documents(uploaded_files)
            print(f"Background processing completed: {result}")
        
        background_tasks.add_task(process_documents)
        
        return UploadResponse(
            message=f"Successfully uploaded {len(uploaded_files)} files. Processing in background...",
            files_processed=len(uploaded_files),
            files=[Path(f).name for f in uploaded_files]
        )
        
    except Exception as e:
        # Clean up uploaded files if processing fails
        for file_path in uploaded_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_documents(chat_message: ChatMessage):
    """Chat with uploaded documents"""
    try:
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Get response from RAG system
        response = rag_system.chat(chat_message.message)
        
        # Store conversation (optional - for session management)
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        chat_sessions[session_id].append({
            "user_message": chat_message.message,
            "bot_response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/documents", response_model=DocumentStats)
async def get_document_stats():
    """Get statistics about uploaded documents"""
    try:
        stats = rag_system.get_document_stats()
        return DocumentStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from the index"""
    try:
        result = rag_system.delete_document(filename)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "history": chat_sessions[session_id]
    }

@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"message": f"Chat history cleared for session {session_id}"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


