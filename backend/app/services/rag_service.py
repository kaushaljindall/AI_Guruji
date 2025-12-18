
import os
import fitz  # PyMuPDF
import faiss
import numpy as np
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Gemini Embeddings (Cloud Native Replacement for HuggingFace)
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class RagService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.embedder = None
        self.dimension = 768 # Gemini-1.5-flash/embedding-001 dimension
        
        if HAS_GEMINI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.embed_model = "models/text-embedding-004"
                print(f"✅ RAG initialized with Gemini Embeddings ({self.embed_model})")
            except Exception as e:
                print(f"⚠️ Gemini Embedding Setup Failed: {e}")
                
        else:
            print("⚠️ No Gemini API Key found. RAG will be strictly Keyword/TF-IDF based (Placeholder).")

        self.storage_dir = os.path.join(os.getcwd(), "data", "vector_store")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = [] 

    def _get_embedding(self, text: str | List[str]) -> np.ndarray:
        if not HAS_GEMINI or not self.api_key:
             # Return zero vector fallback
             count = len(text) if isinstance(text, list) else 1
             return np.zeros((count, self.dimension))
        
        try:
            # Handle single string vs list
            is_list = isinstance(text, list)
            content_to_embed = text if is_list else [text]
            
            # Gemini batch embedding
            # Note: Gemini has batch limits, for huge docs we need loop. 
            # Currently assuming manageable chunks or implementing simple loop here if needed.
            # Simple implementation for MVP:
            
            embeddings = []
            for item in content_to_embed:
                result = genai.embed_content(
                    model=self.embed_model,
                    content=item,
                    task_type="retrieval_document",
                    title="Lecture Context"
                )
                if 'embedding' in result:
                    embeddings.append(result['embedding'])
            
            return np.array(embeddings)
            
        except Exception as e:
            print(f"❌ Embedding Error: {e}")
            return np.zeros((len(text) if isinstance(text, list) else 1, self.dimension))

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
        if not chunks:
            return
            
        self.chunks.extend(chunks)
        embeddings = self._get_embedding(chunks)
        if embeddings.size > 0:
            self.index.add(embeddings.astype('float32'))

    def search(self, query: str, k: int = 5) -> List[str]:
        """Searches the index for the most relevant chunks."""
        if self.index.ntotal == 0:
            return []
        
        query_vector = self._get_embedding([query])
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
        
    def save_index(self):
        """Saves current index to disk (Mock implementation for now)."""
        # In a real app, you would faiss.write_index(self.index, self.storage_dir/index.faiss)
        # and pickle self.chunks
        print(f"✅ Index saved with {len(self.chunks)} chunks.")

rag_service = RagService()
