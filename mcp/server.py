from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")


@app.post("/v1/chat/completions")
async def chat(req: Request):
    body = await req.json()
    prompt = body["messages"][-1]["content"]

    context = get_context(prompt)
    full_prompt = context + "\n\nTASK:\n" + prompt

    return call_llm(full_prompt)


def get_context(query: str):
    # stub: ide jön később Qdrant / index
    return f"[REPO_CONTEXT for: {query}]"


def call_llm(prompt: str):
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
        json={
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
    )
    return r.json()