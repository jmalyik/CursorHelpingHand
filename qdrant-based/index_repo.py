#!/usr/bin/env python3
"""
Initialize Qdrant index for a repo.

Usage:
    python index_repo.py /path/to/repo
    
Environment:
    GEMINI_API_KEY - Required
    QDRANT_URL - Optional, defaults to http://localhost:6333
"""

import os
import sys
from pathlib import Path

# Add mcp directory to path
sys.path.insert(0, str(Path(__file__).parent / "mcp"))

from embeddings import index_repo


def main():
    if len(sys.argv) < 2:
        print("Usage: python index_repo.py /path/to/repo")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    gemini_key = os.getenv("GEMINI_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    if not Path(repo_path).exists():
        print(f"ERROR: Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    print(f"🚀 Starting indexing...")
    print(f"   Repo: {repo_path}")
    print(f"   Qdrant: {qdrant_url}")
    print()
    
    success = index_repo(repo_path, gemini_key, qdrant_url)
    
    if success:
        print("\n✅ Indexing complete!")
        sys.exit(0)
    else:
        print("\n❌ Indexing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
