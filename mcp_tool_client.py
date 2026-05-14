import requests
import json
import sys

MCP_URL = "http://localhost:8000/v1/chat/completions"


def ask(query: str) -> str:
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

        # OpenAI-style response parsing
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"ERROR: {str(e)}"


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(ask(query))
        return

    # interactive mode
    print("MCP Tool Client ready. Type queries:\n")

    while True:
        try:
            q = input(">> ")
            if q.strip().lower() in ["exit", "quit"]:
                break

            print("\n" + ask(q) + "\n")

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()