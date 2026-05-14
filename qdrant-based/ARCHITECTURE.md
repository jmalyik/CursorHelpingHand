# Architecture Overview

## System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          CURSOR CLIENT                          │
│         (OpenAI API endpoint: http://localhost:8000/v1)         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ "How do I authenticate?"
                           │ (User Question)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MCP PROXY (FastAPI)                           │
│                   server.py                                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Extract Query                                         │  │
│  │ 2. Call get_context()                                    │  │
│  │    ├─ Embed query (Gemini)                              │  │
│  │    └─ Search Qdrant for top 3 chunks                    │  │
│  │ 3. Combine context + prompt                             │  │
│  │ 4. Call Gemini API                                       │  │
│  │ 5. Convert response to OpenAI format                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────┬──────────────┘
               │                                  │
          ┌────▼────┐                        ┌────▼──────┐
          │ Qdrant   │                        │ Gemini    │
          │ Vector   │                        │ API       │
          │ Database │                        │           │
          │          │                        │           │
          │ Top K    │                        │ Embeddings│
          │ Search   │                        │ LLM Call  │
          └──────────┘                        └───────────┘
               ▲
               │ Indexed chunks
               │
┌──────────────┴──────────────────────────────────────────────────┐
│              SETUP: Repo Indexing (One-time)                   │
│                                                                 │
│  index_repo.py                                                  │
│  ├─ repo_indexer.py                                            │
│  │  ├─ Parse Python files                                     │
│  │  ├─ Extract functions/classes/imports                      │
│  │  └─ Create logical chunks                                  │
│  │                                                              │
│  └─ embeddings.py                                              │
│     ├─ Generate Gemini embeddings (768-dim)                   │
│     └─ Upload to Qdrant                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. **mcp/server.py** (FastAPI Proxy)
- OpenAI-compatible API endpoint
- Integrates Qdrant semantic search
- Calls Gemini API
- Formats response to OpenAI standard

### 2. **mcp/repo_indexer.py** (Code Parser)
- Intelligent chunking strategy
- Extracts Python/JavaScript functions, classes, imports
- Maintains metadata (file path, line numbers, type)

### 3. **mcp/embeddings.py** (Embedding Service)
- Generates embeddings using Gemini text-embedding-004
- Manages Qdrant collection (create, upload, search)
- Semantic search interface

### 4. **index_repo.py** (Indexing CLI)
- One-time setup script
- Orchestrates: parse → embed → upload
- Usage: `python index_repo.py /path/to/repo`

### 5. **docker-compose.yml**
- Qdrant vector database (port 6333)
- MCP proxy service (port 8000)
- Volume mount for indexing

## Token Savings Mechanism

### Without Context Injection
```
Query: "How do I authenticate?"
→ Full repo context: ~50KB (10,000+ tokens)
→ LLM processes: ~15,000 tokens
→ Response: ~500 tokens
─────────────────────
TOTAL: ~15,500 tokens
```

### With Semantic Search
```
Query: "How do I authenticate?"
→ Embedding generated: <1 token (one-time)
→ Qdrant search: 0 tokens
→ Top 3 chunks: ~500 tokens (only relevant code)
→ LLM processes: ~2,000 tokens
→ Response: ~500 tokens
─────────────────────
TOTAL: ~3,000 tokens
─────────────────────
💰 SAVINGS: ~87% (12,500 tokens saved per query)
```

## Performance Characteristics

| Operation | Time | Cost |
|-----------|------|------|
| Index small repo (50 files) | ~2-5 min | ~$0.05 (Gemini embeddings) |
| Semantic search | <500ms | ~0.001 ¢ |
| LLM response | ~3-5s | ~$0.001-0.005 |
| **Per-query total** | ~5s | ~$0.002 |

## Limitations & Future Work

### Current Limitations
- Max 100 files per indexing run (scalable)
- Supports Python/JavaScript only
- Chunk size limited to 10KB
- No code caching/incremental updates

### Roadmap
1. **Incremental indexing** - Only re-index changed files
2. **Multi-language support** - Go, Java, C++, etc.
3. **Cache layer** - Redis for frequently accessed chunks
4. **Multi-LLM support** - OpenAI, Claude, Vertex AI
5. **Token usage monitoring** - Track savings per query
6. **Codebase-specific prompts** - Auto-detect frameworks
7. **IDE plugins** - VS Code, JetBrains native integration

## Development

### Local Development (Docker)
```bash
export GEMINI_API_KEY="sk-..."

# Build & start services
docker compose up --build

# In another terminal: index repo
docker compose exec mcp python index_repo.py /workspace

# Test
docker compose exec mcp python -c "from mcp_tool_client import ask; print(ask('test'))"
```

### Production Considerations
- Use environment-specific .env files
- Implement API rate limiting
- Add authentication/authorization
- Monitor Qdrant memory usage
- Set up log aggregation
- Use managed Qdrant (Qdrant Cloud) for scale
