import os
import json
import requests
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings

from repo_indexer import CodeChunk


class ChromaEmbeddingService:
    """
    Local vector database using Chroma + Gemini embeddings.
    No Docker required. Stores everything locally in .chroma/
    
    Perfect for 10-500K documents.
    """
    
    def __init__(self, gemini_api_key: str, chroma_dir: str = ".chroma"):
        self.gemini_key = gemini_api_key
        self.chroma_dir = Path(chroma_dir)
        self.chroma_dir.mkdir(exist_ok=True)
        
        # Initialize Chroma with local persistence
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(self.chroma_dir),
            anonymized_telemetry=False,
        )
        self.client = chromadb.Client(settings)
        self.collection_name = "code_chunks"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.embedding_model = "models/text-embedding-004"
        self.chunk_counter = 0
    
    def index_chunks(self, chunks: List[CodeChunk], batch_size: int = 20) -> bool:
        """
        Embed chunks and upload to Chroma.
        Processes in batches for memory efficiency.
        
        Args:
            chunks: List of CodeChunk objects
            batch_size: Process N chunks per batch
        
        Returns:
            True if successful
        """
        try:
            total = len(chunks)
            print(f"📦 Indexing {total} chunks (batch size: {batch_size})")
            
            for i in range(0, total, batch_size):
                batch = chunks[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total + batch_size - 1) // batch_size
                
                print(f"  Batch {batch_num}/{total_batches}...", end=" ", flush=True)
                
                # Generate embeddings for batch
                ids = []
                embeddings = []
                metadatas = []
                documents = []
                
                for chunk in batch:
                    embedding = self._get_embedding(chunk.content)
                    
                    if embedding is None:
                        print(f"\n  ⚠️  Skipped: {chunk.chunk_id}")
                        continue
                    
                    ids.append(chunk.chunk_id)
                    embeddings.append(embedding)
                    documents.append(chunk.content)
                    metadatas.append({
                        "file_path": chunk.file_path,
                        "chunk_type": chunk.chunk_type,
                        "language": chunk.language,
                        "start_line": str(chunk.start_line),
                        "end_line": str(chunk.end_line),
                    })
                    self.chunk_counter += 1
                
                # Upload to Chroma
                if ids:
                    self.collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        documents=documents,
                        metadatas=metadatas
                    )
                    print(f"✓ {len(ids)} chunks")
            
            # Persist to disk
            self.client.persist()
            
            print(f"\n✅ Total indexed: {self.chunk_counter} chunks")
            print(f"💾 Saved to: {self.chroma_dir.absolute()}")
            return True
            
        except Exception as e:
            print(f"\n❌ Error indexing chunks: {e}")
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
                print("⚠️  Failed to embed query")
                return []
            
            # Search in Chroma
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results or not results["ids"] or len(results["ids"]) == 0:
                return []
            
            search_results = []
            for i, chunk_id in enumerate(results["ids"][0]):
                # Chroma returns distances (0-2), convert to similarity score (0-1)
                distance = results["distances"][0][i]
                similarity = 1 - (distance / 2)  # Cosine distance normalization
                
                search_results.append({
                    "score": similarity,
                    "chunk_id": chunk_id,
                    "file_path": results["metadatas"][0][i]["file_path"],
                    "chunk_type": results["metadatas"][0][i]["chunk_type"],
                    "content": results["documents"][0][i],
                    "language": results["metadatas"][0][i]["language"],
                })
            
            return search_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection": self.collection_name,
                "location": str(self.chroma_dir.absolute()),
                "size_mb": self._get_dir_size_mb(self.chroma_dir)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def clear(self) -> bool:
        """Clear all indexed chunks (for re-indexing)"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.client.persist()
            print("✅ Collection cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing collection: {e}")
            return False
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
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
            print(f"❌ Embedding error: {e}")
            return None
    
    def _get_dir_size_mb(self, path: Path) -> float:
        """Calculate directory size in MB"""
        total = 0
        for p in path.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
        return total / (1024 * 1024)


def index_repo(repo_path: str, gemini_key: str, chroma_dir: str = ".chroma", clear_existing: bool = False):
    """
    Convenience function to index entire repo.
    
    Usage:
        from chroma import index_repo
        index_repo("/path/to/repo", os.getenv("GEMINI_API_KEY"))
    """
    from repo_indexer import RepoIndexer
    
    print(f"🔍 Indexing repo: {repo_path}")
    print(f"📍 Vector DB: {chroma_dir}\n")
    
    # Initialize service
    embed_service = ChromaEmbeddingService(gemini_key, chroma_dir)
    
    # Clear if requested
    if clear_existing:
        embed_service.clear()
    
    # Parse and chunk
    indexer = RepoIndexer(repo_path)
    chunks = indexer.index_repo(max_files=500)  # Increased for larger repos
    
    if not chunks:
        print("⚠️  No code chunks found")
        return False
    
    # Generate embeddings and upload
    success = embed_service.index_chunks(chunks)
    
    if success:
        stats = embed_service.get_stats()
        print(f"\n📊 Stats:")
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Location: {stats['location']}")
        print(f"   Size: {stats['size_mb']:.1f} MB")
    
    return success
