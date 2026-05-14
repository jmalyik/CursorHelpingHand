# 🔌 Minimal MCP Context Stack (Cursor + Python Proxy)

Ez egy minimál AI coding stack nagy kódbázisokhoz, ami:

- csökkenti a token usage-et
- repo-kontrollált contextet ad LLM-nek
- Cursorral együtt használható
- egyetlen MCP proxy service-re épül

Nincs microservice zoo. Nincs overengineering.

---

# 🧠 Lényege

Cursor nem a teljes repo-t küldi az LLM-nek.

Hanem:

Cursor
-> MCP Proxy (Python)
-> (context injection)
-> LLM (Gemini / OpenAI)

---

# ⚙️ Komponensek

## 1. MCP Proxy (egy Python service)

Feladata:

- prompt fogadása
- repo context lekérdezés (stub / később Qdrant)
- prompt + context összefűzés
- LLM hívás
- OpenAI-compatible válasz visszaadása Cursornak

---

## 2. Qdrant (opcionális, későbbi bővítés)

:contentReference[oaicite:0]{index=0}

- semantic search
- repo embedding storage
- releváns kód chunkok visszakeresése

---

## 3. Cursor (client)

:contentReference[oaicite:1]{index=1}

- OpenAI API-t hív
- nem tud a MCP-ről
- csak “jobb válaszokat” kap

---

# 🐳 Docker setup

## 📁 struktúra

```text
.
├── docker-compose.yml
└── mcp/
    ├── Dockerfile
    ├── server.py
    └── requirements.txt
```

## Futtatás

```
docker compose up --build
```

### Cursor integráció

```
Base URL:
http://localhost:8000/v1

API key:
anything
```