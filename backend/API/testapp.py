import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import faiss
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.prompts import PromptTemplate
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import load_index_from_storage
from langchain_huggingface import HuggingFaceEmbeddings
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv

load_dotenv()

class SimpleDocumentRAG:
    def __init__(self, 
                 storage_dir: str = "./storage",
                 data_dir: str = "./data",
                 embedding_model: str = "text-embedding-ada-002"):
        
        self.storage_dir = Path(storage_dir)
        self.data_dir = Path(data_dir)
        self.embedding_model_name = embedding_model
        self.metadata_file = self.storage_dir / "file_metadata.json"
        
        # Create directories
        self.storage_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize models
        self._setup_models()
        
        # Load or create index
        self.index = self._load_or_create_index()
        
        # Setup chat engine
        self.chat_engine = None
        self._setup_chat_engine()
    
    def _setup_models(self):
        """Initialize LLM and embedding models"""
        self.llm = OpenAI(model="gpt-4o-mini", temperature=0, max_tokens=512)
        self.embed_model = OpenAIEmbedding(model_name=self.embedding_model_name)
        self.text_splitter = SentenceSplitter(chunk_size=800, chunk_overlap=60)
        
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.text_splitter = self.text_splitter
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash for file content to detect changes"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _load_file_metadata(self) -> Dict:
        """Load existing file metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_file_metadata(self, metadata: Dict):
        """Save file metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _get_files_to_process(self) -> List[Path]:
        """Identify new or modified files that need processing"""
        current_files = list(self.data_dir.rglob("*"))
        current_files = [f for f in current_files if f.is_file() and f.suffix.lower() in ['.pdf', '.docx', '.md', '.txt','.csv']]
        
        existing_metadata = self._load_file_metadata()
        files_to_process = []
        
        for file_path in current_files:
            file_key = str(file_path.relative_to(self.data_dir))
            current_hash = self._get_file_hash(file_path)
            current_mtime = file_path.stat().st_mtime
            
            # Check if file is new or modified
            if (file_key not in existing_metadata or 
                existing_metadata[file_key].get('hash') != current_hash or
                existing_metadata[file_key].get('mtime') != current_mtime):
                files_to_process.append(file_path)
        
        return files_to_process
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        # Check if index exists
        if (self.storage_dir / "docstore.json").exists():
            try:
                # Create FAISS vector store
                d = 1536  # BGE small embedding dimension
                faiss_index = faiss.IndexFlatL2(d)
                vector_store = FaissVectorStore(faiss_index=faiss_index)
                
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_store, 
                    persist_dir=str(self.storage_dir)
                )
                index = load_index_from_storage(storage_context=storage_context)
                print("✅ Loaded existing index")
                return index
            except Exception as e:
                print(f"⚠️ Error loading index: {e}")
                print("Creating new index...")
        
        # Create new index
        return self._create_new_index()
    
    def _create_new_index(self):
        """Create a new vector index"""
        d = 1536  # BGE small embedding dimension
        faiss_index = faiss.IndexFlatL2(d)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create empty index
        index = VectorStoreIndex([], storage_context=storage_context)
        print("✅ Created new empty index")
        return index
    
    def add_documents(self, file_paths: Optional[List[str]] = None) -> Dict:
        """Add new documents to the index"""
        if file_paths:
            # Process specific files
            files_to_process = [Path(fp) for fp in file_paths if Path(fp).exists()]
        else:
            # Process all new/modified files
            files_to_process = self._get_files_to_process()
        
        if not files_to_process:
            return {"message": "No new files to process", "files_processed": 0}
        
        print(f"📄 Processing {len(files_to_process)} files...")
        
        # Load documents
        documents = []
        for file_path in files_to_process:
            try:
                reader = SimpleDirectoryReader(
                    input_files=[str(file_path)],
                    file_metadata=lambda x: {
                        'source': str(file_path),
                        'filename': file_path.name,
                        'upload_time': datetime.now().isoformat()
                    }
                )
                docs = reader.load_data()
                documents.extend(docs)
                print(f"✅ Loaded: {file_path.name}")
            except Exception as e:
                print(f"❌ Error loading {file_path.name}: {e}")
        
        if not documents:
            return {"message": "No documents could be loaded", "files_processed": 0}
        
        # Add to existing index
        for doc in documents:
            self.index.insert(doc)
        
        # Persist the updated index (LlamaIndex handles this automatically)
        self.index.storage_context.persist(persist_dir=str(self.storage_dir))
        
        # Update metadata
        metadata = self._load_file_metadata()
        for file_path in files_to_process:
            file_key = str(file_path.relative_to(self.data_dir))
            metadata[file_key] = {
                'hash': self._get_file_hash(file_path),
                'mtime': file_path.stat().st_mtime,
                'processed_at': datetime.now().isoformat(),
                'filename': file_path.name
            }
        self._save_file_metadata(metadata)
        
        # Recreate chat engine with updated index
        self._setup_chat_engine()
        
        return {
            "message": f"Successfully processed {len(files_to_process)} files",
            "files_processed": len(files_to_process),
            "files": [fp.name for fp in files_to_process]
        }
    
    def _setup_chat_engine(self):
        """Setup chat engine with custom prompt"""
        system_prompt = """You are an AI assistant named Alex that answers questions based on the provided documents. Rules:
        - Generate human readable output, avoid gibberish text
        - Be concise and direct, no more than 3 sentences unless more detail is needed
        - If you don't know something from the context, say "I don't know"
        - Use professional business language
        - Never include offensive language
        - Ensure accuracy based on the provided context only
        
        Question: {query_str}
        Context: {context_str}
        Answer:"""
        
        memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
        
        self.chat_engine = self.index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=system_prompt,
            similarity_top_k=5
        )
    
    def chat(self, message: str) -> str:
        """Chat with the documents"""
        if not self.chat_engine:
            return "❌ Chat engine not initialized. Please add some documents first."
        
        try:
            response = self.chat_engine.chat(message)
            return str(response)
        except Exception as e:
            return f"❌ Error processing query: {str(e)}"
    
    def query(self, question: str) -> str:
        """One-time query without chat memory"""
        try:
            query_engine = self.index.as_query_engine(similarity_top_k=5)
            response = query_engine.query(question)
            return str(response)
        except Exception as e:
            return f"❌ Error processing query: {str(e)}"
    
    def get_document_stats(self) -> Dict:
        """Get statistics about indexed documents"""
        metadata = self._load_file_metadata()
        return {
            "total_files": len(metadata),
            "files": list(metadata.keys()),
            "last_updated": max([m.get('processed_at', '') for m in metadata.values()]) if metadata else None,
            "index_size": len(self.index.docstore.docs) if hasattr(self.index, 'docstore') else 0
        }

    def delete_document(self, filename: str) -> Dict:
        """Delete a document from the index"""
        try:
        # Get relative path to match metadata keys
            file_path = self.data_dir / filename
            file_key = str(file_path.relative_to(self.data_dir))
        
            metadata = self._load_file_metadata()
        
            if file_key not in metadata:
                return {"error": f"File {filename} not found in index"}
        
            # Remove document from index (LlamaIndex implementation)
            ref_doc_id = metadata[file_key].get("doc_id")
            if ref_doc_id and hasattr(self.index, "delete_ref_doc"):
                self.index.delete_ref_doc(ref_doc_id)
        
            # Delete file and metadata
            if file_path.exists():
                file_path.unlink()
            del metadata[file_key]
            
            self._save_file_metadata(metadata)
            self.index.storage_context.persist()
            
            return {"message": f"Deleted {filename} successfully"}
        except Exception as e:
            return {"error": f"Deletion failed: {str(e)}"}
    
# Usage Example
if __name__ == "__main__":
    # Initialize the system
    rag = SimpleDocumentRAG(
        storage_dir="./storage",
        data_dir="./data"
    )
    
    # Add documents (processes only new/modified files)
    result = rag.add_documents()
    print(f"📊 {result}")
    
    # Chat with documents
    while True:
        question = input("\n💬 Ask a question (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
        
        response = rag.chat(question)
        print(f"🤖 {response}")
        
        # Show stats
        stats = rag.get_document_stats()
        print(f"📈 Stats: {stats['total_files']} files indexed")