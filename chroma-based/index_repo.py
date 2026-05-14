#!/usr/bin/env python3
"""
Initialize Chroma index for a repo.

Usage:
    python index_repo.py /path/to/repo

Environment:
    GEMINI_API_KEY - Required
"""

import os
import sys
from pathlib import Path

# Add mcp directory to path
sys.path.insert(0, str(Path(__file__).parent / "mcp"))

from chroma import index_repo


def main():
    if len(sys.argv) < 2:
        print("Usage: python index_repo.py /path/to/repo [--clear]")
        print("\nExample:")
        print("  python index_repo.py /home/user/myproject")
        print("  python index_repo.py . --clear  # Re-index current directory")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    clear_existing = "--clear" in sys.argv
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export GEMINI_API_KEY='sk-...'  # Linux/Mac")
        print("  set GEMINI_API_KEY=sk-...        # Windows")
        sys.exit(1)
    
    if not Path(repo_path).exists():
        print(f"❌ ERROR: Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("🚀 CHROMA REPO INDEXER (Local Vector DB)")
    print("=" * 60)
    print(f"📂 Repo: {Path(repo_path).absolute()}")
    print(f"💾 Storage: {Path('.chroma').absolute()}")
    print(f"🔑 API Key: {gemini_key[:10]}...")
    
    if clear_existing:
        print(f"🔄 Mode: Re-index (clear existing)")
    
    print()
    
    success = index_repo(repo_path, gemini_key, chroma_dir=".chroma", clear_existing=clear_existing)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS - Ready to use!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("  1. Start MCP server:")
        print("     docker build -t mcp-chroma ./mcp")
        print("     docker run -p 8000:8000 -v $(pwd)/.chroma:/app/.chroma mcp-chroma")
        print("\n  2. Configure Cursor:")
        print("     Base URL: http://localhost:8000/v1")
        print("     API Key: (anything)")
        print("\n  3. Start asking!")
        sys.exit(0)
    else:
        print("\n❌ FAILED - Check errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
