from flask import Flask, request
import requests
import os

app = Flask(__name__)

@app.post("/generate")
def generate():
    data = request.json

    prompt = data["prompt"]

    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
        json={
            "contents": [{"parts": [{"text": prompt}]}]
        }
    )

    return r.json()