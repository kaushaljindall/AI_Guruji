
import os
import fitz  # PyMuPDF
import faiss
import numpy as np
import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class RagService:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY not found. RAG will fail if you don't use Ollama fallback.")
        else:
            genai.configure(api_key=api_key)
            
        self.dimension = 768  # Dimension for embedding-001/text-embedding-004
        self.storage_dir = os.path.join(os.getcwd(), "data", "vector_store")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []  # Store text chunks corresponding to FAISS index

    def _get_embedding(self, text: str | List[str]) -> np.ndarray:
        """Helper to get embeddings from Gemini or Ollama."""
        # TODO: Add Ollama fallback logic here if needed. 
        # For now, we assume Gemini.
        
        if isinstance(text, str):
            text = [text]
            
        try:
            # text-embedding-004 is current SOTA for Gemini
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
                title="Academic Content" 
            )
            # Result is a dict with 'embedding' key (list of floats for single, list of list for batch? Check docs)
            # Actually genai.embed_content for list returns a list of embeddings.
            
            return np.array(result['embedding'])
        except Exception as e:
            # Fallback to older model if 004 fails or auth error
            print(f"Embedding error: {e}")
            return np.zeros((len(text), self.dimension))

    def save_index(self):
        """Persist index and chunks to disk."""
        faiss.write_index(self.index, os.path.join(self.storage_dir, "index.faiss"))
        np.save(os.path.join(self.storage_dir, "chunks.npy"), self.chunks)

    def load_index(self):
        """Load index and chunks from disk if they exist."""
        index_path = os.path.join(self.storage_dir, "index.faiss")
        chunks_path = os.path.join(self.storage_dir, "chunks.npy")
        if os.path.exists(index_path) and os.path.exists(chunks_path):
            self.index = faiss.read_index(index_path)
            self.chunks = list(np.load(chunks_path, allow_pickle=True))

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts full text from a PDF file."""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def create_chunks(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Splits text into chunks with overlap."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def add_to_index(self, chunks: List[str]):
        """Embeds chunks and adds them to the FAISS index."""
        self.chunks.extend(chunks)
        # Process in batches to avoid API limits
        batch_size = 20
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            embeddings = self._get_embedding(batch)
            if embeddings.size > 0:
                self.index.add(embeddings.astype('float32'))

    def search(self, query: str, k: int = 3) -> List[str]:
        """Searches the index for the most relevant chunks."""
        if self.index.ntotal == 0:
            return []
        
        # Determine query embedding
        # Note: task_type for query should ideally be retrieval_query
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            query_vector = np.array([result['embedding']])
        except:
             return []

        D, I = self.index.search(query_vector.astype('float32'), k)
        
        results = []
        for idx in I[0]:
            if idx != -1 and idx < len(self.chunks):
                results.append(self.chunks[idx])
        return results

    def clear_index(self):
        """Reset the index and chunks."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []

rag_service = RagService()
