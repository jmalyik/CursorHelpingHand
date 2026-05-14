import os
import json
import requests
from typing import List, Dict
from repo_indexer import CodeChunk


class EmbeddingService:
    """
    Generate embeddings using Gemini API and store in Qdrant.
    """
    
    def __init__(self, gemini_api_key: str, qdrant_url: str = "http://localhost:6333"):
        self.gemini_key = gemini_api_key
        self.qdrant_url = qdrant_url
        self.collection_name = "code_chunks"
        self.embedding_model = "models/text-embedding-004"
    
    def index_chunks(self, chunks: List[CodeChunk]) -> bool:
        """
        Embed chunks and upload to Qdrant.
        
        Returns:
            True if successful
        """
        try:
            # Ensure collection exists
            self._ensure_collection()
            
            # Generate embeddings for chunks
            points = []
            for i, chunk in enumerate(chunks):
                embedding = self._get_embedding(chunk.content)
                
                if embedding is None:
                    print(f"Warning: Failed to embed chunk {chunk.chunk_id}")
                    continue
                
                point = {
                    "id": i,
                    "vector": embedding,
                    "payload": {
                        "file_path": chunk.file_path,
                        "chunk_id": chunk.chunk_id,
                        "chunk_type": chunk.chunk_type,
                        "content": chunk.content,
                        "language": chunk.language,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                    }
                }
                points.append(point)
                
                # Upload in batches
                if len(points) >= 10:
                    self._upload_points(points)
                    points = []
            
            # Upload remaining points
            if points:
                self._upload_points(points)
            
            print(f"✅ Indexed {len(chunks)} chunks to Qdrant")
            return True
            
        except Exception as e:
            print(f"❌ Error indexing chunks: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant chunks using semantic search.
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of relevant chunks with scores
        """
        try:
            query_embedding = self._get_embedding(query)
            if query_embedding is None:
                print("Failed to embed query")
                return []
            
            response = requests.post(
                f"{self.qdrant_url}/collections/{self.collection_name}/points/search",
                json={
                    "vector": query_embedding,
                    "limit": top_k,
                    "with_payload": True
                },
                timeout=30
            )
            response.raise_for_status()
            
            results = []
            for hit in response.json()["result"]:
                results.append({
                    "score": hit["score"],
                    "chunk_id": hit["payload"]["chunk_id"],
                    "file_path": hit["payload"]["file_path"],
                    "chunk_type": hit["payload"]["chunk_type"],
                    "content": hit["payload"]["content"],
                    "language": hit["payload"]["language"],
                })
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini API."""
        try:
            # Truncate text to avoid API limits
            text = text[:8000]
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.embedding_model}:embedContent?key={self.gemini_key}",
                json={
                    "model": self.embedding_model,
                    "content": {
                        "parts": [{"text": text}]
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            embedding = data.get("embedding", {}).get("values", None)
            return embedding
            
        except Exception as e:
            print(f"Embedding error for text chunk: {e}")
            return None
    
    def _ensure_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        try:
            # Check if collection exists
            response = requests.get(
                f"{self.qdrant_url}/collections/{self.collection_name}",
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Collection '{self.collection_name}' exists")
                return
            
        except:
            pass
        
        # Create collection
        try:
            requests.put(
                f"{self.qdrant_url}/collections/{self.collection_name}",
                json={
                    "vectors": {
                        "size": 768,  # Gemini embedding size
                        "distance": "Cosine"
                    }
                },
                timeout=30
            )
            print(f"✅ Created collection '{self.collection_name}'")
        except Exception as e:
            print(f"⚠️  Failed to create collection: {e}")
    
    def _upload_points(self, points: List[Dict]):
        """Upload points to Qdrant."""
        try:
            response = requests.put(
                f"{self.qdrant_url}/collections/{self.collection_name}/points",
                json={"points": points},
                timeout=30
            )
            response.raise_for_status()
            print(f"  Uploaded {len(points)} points")
        except Exception as e:
            print(f"Error uploading points: {e}")


def index_repo(repo_path: str, gemini_key: str, qdrant_url: str = "http://localhost:6333"):
    """
    Convenience function to index entire repo.
    
    Usage:
        from embeddings import index_repo
        index_repo("/path/to/repo", os.getenv("GEMINI_API_KEY"))
    """
    from repo_indexer import RepoIndexer
    
    print(f"🔍 Indexing repo: {repo_path}")
    
    # Parse and chunk
    indexer = RepoIndexer(repo_path)
    chunks = indexer.index_repo(max_files=100)
    
    if not chunks:
        print("⚠️  No code chunks found")
        return False
    
    # Generate embeddings and upload
    embed_service = EmbeddingService(gemini_key, qdrant_url)
    return embed_service.index_chunks(chunks)
