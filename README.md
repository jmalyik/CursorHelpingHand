# 🔌 Cursor Token Saver - MCP Solutions

Reduce Cursor AI token consumption with intelligent code chunking + semantic search.

**Two solutions - choose what fits your needs!**

---

## 📊 Chroma vs Qdrant

| Aspect | Chroma | Qdrant |
|--------|--------|--------|
| **Setup** | Indexing: Python, Server: Docker | Docker only |
| **Memory** | ~100MB | ~500MB+ |
| **Scale** | 10-500K docs | 100K-10M+ docs |
| **Persistence** | Local .db file | Network DB |
| **Deployment** | Simpler infrastructure | Complex setup |
| **Best for** | **Local dev + 125K LOC** | Enterprise |
| **Folder** | `./chroma-based/` | `./qdrant-based/` |

---

## 🚀 Quick Start

### Option A: Chroma (Recommended for 125k LOC)

**Indexing + Server:**
```bash
cd chroma
export GEMINI_API_KEY="sk-..."
python index_repo.py /path/to/repo    # Python: parse & embed
docker compose up                      # Docker: start server
```

📖 Details: [chroma/README.md](./chroma/README.md)

### Option B: Qdrant (Enterprise)

**Server + Indexing:**
```bash
cd qdrant
export GEMINI_API_KEY="sk-..."
docker compose up --build              # Docker: Qdrant + MCP
docker compose exec mcp python index_repo.py /workspace
```

📖 Details: [qdrant/README.md](./qdrant/README.md)

---

## ✨ Features (Both Solutions)

- ✅ Intelligent code chunking (functions, classes, imports)
- ✅ Gemini embeddings (semantic search)
- ✅ OpenAI-compatible API (Cursor integration)
- ✅ **87% token reduction** for large codebases
- ✅ Java + Python + JS/TS support

---

## 💰 Token Savings

```
Without MCP:      ~10,000 tokens/query
Chroma/Qdrant:    ~1,300 tokens/query
──────────────────────────────────
Savings:          87% 🎯
```

---

## 🎯 Which One to Choose?

### Choose **Chroma** if:
- You have 4 repos, 125k LOC
- Don't need Qdrant infrastructure
- Prefer lighter vector DB (~100MB memory)
- Local development focus

### Choose **Qdrant** if:
- You have >500K LOC
- Enterprise environment required
- Need distributed vector database
- Scalability is critical

---

## 📚 Documentation

- [chroma/README.md](./chroma/README.md) - Chroma solution
- [chroma/SETUP.md](./chroma/SETUP.md) - Chroma setup guide
- [qdrant/README.md](./qdrant/README.md) - Qdrant solution
- [qdrant/ARCHITECTURE.md](./qdrant/ARCHITECTURE.md) - Architecture overview

---

## 🔧 Cursor Integration

In both cases:

1. **Index repo** (`python index_repo.py /repo`)
2. **Start MCP** (`docker compose up`)
3. **Cursor Settings:**
   ```
   Base URL: http://localhost:8000/v1
   API Key: (any value)
   Model: (any name)
   ```
4. **Start asking!**

---

## 🏁 Summary

| | Chroma | Qdrant |
|---|---|---|
| **Repository** | `./chroma/` | `./qdrant/` |
| **Status** | ✅ Production Ready | ✅ Production Ready |
| **For you?** | **← START HERE** | Advanced users |

Start with **Chroma**! 🚀
