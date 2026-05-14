#!/usr/bin/env python3
"""
MCP Tool Client for testing the Chroma-enabled MCP proxy.

Usage:
    python mcp_tool_client.py "What does this code do?"
"""

import requests
import json
import sys


MCP_URL = "http://localhost:8000/v1/chat/completions"


def ask(query: str) -> str:
    """Send query to MCP proxy and get response."""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ]
    }

    try:
        r = requests.post(MCP_URL, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()

        # OpenAI-compatible response parsing
        if "choices" in data and len(data["choices"]) > 0:
            message = data["choices"][0].get("message", {})
            content = message.get("content", "")
            if content:
                return content
        
        # Fallback if response structure is unexpected
        return f"⚠️  Unexpected response format:\n{json.dumps(data, indent=2)}"

    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to MCP proxy. Is it running on port 8000?\n\nStart it with: docker compose up"
    except requests.exceptions.Timeout:
        return "❌ Request timeout. LLM response took too long."
    except json.JSONDecodeError:
        return "❌ Invalid JSON response from proxy."
    except Exception as e:
        return f"❌ ERROR: {str(e)}"


def get_health():
    """Check MCP server health and stats."""
    try:
        r = requests.get("http://localhost:8000/v1/health", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        
        if query == "--health":
            print("🏥 MCP Server Health:")
            health = get_health()
            print(json.dumps(health, indent=2))
            return
        
        print(f"🤖 Query: {query}\n")
        print("⏳ Waiting for response...\n")
        result = ask(query)
        print(result)
        return

    # Interactive mode
    print("=" * 60)
    print("🔌 MCP Tool Client (Chroma Edition)")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  query        - Ask a question about the codebase")
    print("  health       - Check server status")
    print("  exit/quit    - Exit interactive mode")
    print()
    
    # Check health first
    health = get_health()
    if "error" in health:
        print("⚠️  WARNING: Cannot connect to MCP proxy!")
        print("    Make sure it's running: docker compose up\n")
    else:
        stats = health.get("vector_db", {})
        print(f"✅ Connected to MCP server")
        print(f"   Chunks indexed: {stats.get('total_chunks', '?')}")
        print(f"   Storage: {stats.get('location', '?')}\n")
    
    while True:
        try:
            query = input(">> ").strip()
            
            if not query:
                continue
            
            if query.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
            
            if query.lower() == "health":
                health = get_health()
                print(json.dumps(health, indent=2))
                print()
                continue
            
            print("\n⏳ Searching repo + calling LLM...\n")
            result = ask(query)
            print(result)
            print()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    main()
