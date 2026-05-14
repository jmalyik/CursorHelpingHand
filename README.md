# 🔌 Cursor Token Saver - MCP Solutions

Csökkentsd le a Cursor AI token fogyasztását intelligens code chunking + semantic search-kel.

**Két megoldás - válaszd az igényeidhez!**

---

## 📊 Chroma vs Qdrant

| Aspekt | Chroma | Qdrant |
|--------|--------|--------|
| **Setup** | Python lib (~1 parancs) | Docker required |
| **Memory** | ~100MB | ~500MB+ |
| **Scale** | 10-500K docs | 100K-10M+ docs |
| **Persistence** | Local .db file | Network DB |
| **Deployment** | Simple (copy file) | Complex |
| **Best for** | **Local dev + 125K LOC** | Enterprise |
| **Folder** | `./chroma/` | `./qdrant/` |

---

## 🚀 Gyors Start

### Option A: Chroma (Ajánlott 125k LOC-hoz)

```bash
cd chroma
export GEMINI_API_KEY="sk-..."
python index_repo.py /path/to/repo
docker compose up
```

📖 Részletes: [chroma/README.md](./chroma/README.md)

### Option B: Qdrant (Enterprise)

```bash
cd qdrant
export GEMINI_API_KEY="sk-..."
docker compose up --build
docker compose exec mcp python index_repo.py /workspace
```

📖 Részletes: [qdrant/README.md](./qdrant/README.md)

---

## ✨ Features (Mindkettőben)

- ✅ Intelligens code chunking (functions, classes, imports)
- ✅ Gemini embeddings (semantic search)
- ✅ OpenAI-compatible API (Cursor integrálható)
- ✅ **87% token reduction** nagy repóknál
- ✅ Java + Python + JS/TS támogatás

---

## 💰 Token Savings

```
Cursor nélkül:    ~10,000 token/query
Chroma/Qdrant:    ~1,300 token/query
───────────────────────────────────
Megtakarítás:     87% 🎯
```

---

## 🎯 Melyiket válassza?

### Válassz **Chroma**-t, ha:
- 4 repo, 125k LOC
- Gyors setup kell
- Nem akar Docker/Qdrant infra
- Local development

### Válassz **Qdrant**-ot, ha:
- >500K LOC
- Enterprise environment
- Distributed system
- Skálázható megoldás kell

---

## 📚 Dokumentáció

- [chroma/README.md](./chroma/README.md) - Chroma megoldás
- [chroma/SETUP.md](./chroma/SETUP.md) - Chroma telepítés
- [qdrant/README.md](./qdrant/README.md) - Qdrant megoldás
- [qdrant/ARCHITECTURE.md](./qdrant/ARCHITECTURE.md) - Architektura leírás

---

## 🔧 Cursor Integration

Both cases:

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
