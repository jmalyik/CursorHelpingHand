from fastapi import FastAPI, Request
import os
import requests
from embeddings import EmbeddingService

app = FastAPI()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Initialize embedding service
embed_service = EmbeddingService(GEMINI_KEY, QDRANT_URL)


@app.post("/v1/chat/completions")
async def chat(req: Request):
    body = await req.json()
    prompt = body["messages"][-1]["content"]

    context = get_context(prompt)
    full_prompt = context + "\n\nTASK:\n" + prompt

    gemini_response = call_llm(full_prompt)
    return format_response_to_openai(gemini_response)


def get_context(query: str) -> str:
    """
    Retrieve relevant context from Qdrant using semantic search.
    Returns top 3 relevant code chunks.
    """
    try:
        results = embed_service.search(query, top_k=3)
        
        if not results:
            return "[No relevant context found]"
        
        context_parts = ["[REPO_CONTEXT - Semantic Search Results]"]
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"\n--- Chunk {i} (score: {result['score']:.2f}) ---")
            context_parts.append(f"File: {result['file_path']}")
            context_parts.append(f"Type: {result['chunk_type']}")
            context_parts.append(f"```{result['language']}\n{result['content']}\n```")
        
        context_parts.append("\n[/REPO_CONTEXT]")
        return "\n".join(context_parts)
        
    except Exception as e:
        return f"[Context retrieval error: {str(e)}]"


def call_llm(prompt: str):
    """Call Gemini API"""
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
            json={
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            },
            timeout=60
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def format_response_to_openai(gemini_response: dict):
    """Convert Gemini response format to OpenAI-compatible format"""
    try:
        if "error" in gemini_response:
            error_msg = gemini_response["error"]
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": f"Error: {error_msg}"
                    }
                }]
            }
        
        # Extract text from Gemini response
        text = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
        
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": text
                }
            }]
        }
    except (KeyError, IndexError, TypeError) as e:
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": f"Response parsing error: {str(e)}"
                }
            }]
        }