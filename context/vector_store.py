import os
import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

class VectorStore:
    """Manages local Qdrant vector database for semantic code search."""
    
    def __init__(self, collection_name="project_code"):
        # Initialize Qdrant in local-disk mode (no Docker needed)
        self.client = QdrantClient(path="storage/vector_db")
        self.collection_name = collection_name
        self.embedding_model = "nomic-embed-text"
        self.ollama_url = "http://localhost:11434/api/embeddings"
        
        # Ensure collection exists
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            print(f"📦 Creating new Qdrant collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=768, # Nomic-embed-text size
                    distance=models.Distance.COSINE
                )
            )

    def get_embeddings(self, text):
        """Fetches embeddings from local Ollama instance."""
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.embedding_model, "prompt": text}
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"❌ Embedding Error: {e}")
            return None

    def upsert_code_chunks(self, chunks, metadata_list):
        """Vectorizes and stores code chunks in Qdrant."""
        points = []
        for i, (chunk, meta) in enumerate(zip(chunks, metadata_list)):
            vector = self.get_embeddings(chunk)
            if vector:
                # Use a combined string of repo + path + index as ID
                point_id = hash(f"{meta['repo']}_{meta['path']}_{i}") % (2**63 - 1)
                points.append(models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": chunk,
                        **meta
                    }
                ))
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return len(points)
        return 0

    def semantic_search(self, query, limit=5):
        """Performs semantic search across all indexed code."""
        query_vector = self.get_embeddings(query)
        if not query_vector:
            return []
            
        # Standard search for Qdrant local/cloud
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )
        
        return [res.payload for res in response.points]

class SemanticCodeSplitter:
    """Intelligently splits code based on language syntax to preserve logic."""
    
    @staticmethod
    def split(content, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        
        # Map extension to LangChain Language
        lang_map = {
            ".py": Language.PYTHON,
            ".js": Language.JS,
            ".ts": Language.TS,
            ".go": Language.GO,
            ".java": Language.JAVA,
            ".cpp": Language.CPP,
            ".html": Language.HTML,
        }
        
        language = lang_map.get(ext)
        
        if language:
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=language,
                chunk_size=800,
                chunk_overlap=100
            )
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=100
            )
            
        return splitter.split_text(content)
