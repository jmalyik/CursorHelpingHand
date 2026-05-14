# Setup Guide - Chroma MCP Stack

## Prerequisites

- Python 3.8+
- Docker & Docker Compose (optional, for easy deployment)
- Gemini API key (free: https://ai.google.dev/)
- 200MB disk space (for Chroma index)

---

## Step 1: Get Gemini API Key

1. Go to https://ai.google.dev/
2. Sign in with Google account
3. Create new API key
4. Copy the key

---

## Step 2: Local Setup (No Docker)

### Install Python dependencies

```bash
cd chroma/mcp
pip install -r requirements.txt
```

### Index your repository

```bash
export GEMINI_API_KEY="sk-..."
cd chroma
python index_repo.py /path/to/your/repo
```

**Wait for completion (~2-5 minutes for 100 files)**

Output example:
```
✅ Indexed 145 files → 2847 chunks
📊 Stats:
   Total chunks: 2847
   Location: /path/to/.chroma
   Size: 45.3 MB
```

### Start MCP server

```bash
cd chroma/mcp
python server.py
```

Server running on `http://localhost:8000`

---

## Step 3: Docker Setup (Recommended)

### Build and run

```bash
cd chroma
export GEMINI_API_KEY="sk-..."

# Index (one-time)
python index_repo.py /path/to/your/repo

# Start server
docker compose up --build
```

Server running on `http://localhost:8000`

---

## Step 4: Configure Cursor

1. Open Cursor Settings
2. Find "OpenAI" section
3. Add new provider:
   ```
   Provider: OpenAI (custom)
   Base URL: http://localhost:8000/v1
   API Key: (any value, e.g., "dummy")
   Model: (any name, e.g., "gemini")
   ```
4. Save

---

## Step 5: Test

### Via CLI

```bash
cd chroma
python -c "
from mcp_tool_client import ask
print(ask('What does main() function do?'))
"
```

### Via HTTP

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "role": "user",
      "content": "Explain authentication in this repo"
    }]
  }'
```

### Via Cursor

1. Open Cursor chat
2. Ask: "How does this repo handle authentication?"
3. Should see relevant code + LLM answer

---

## Step 6: Re-Index When Code Changes

For large repos, re-indexing takes time. Options:

### Option A: Re-index entire repo
```bash
python index_repo.py /path/to/repo --clear
```

### Option B: Incremental (future)
Currently: full re-index
Future: Only changed files

---

## Configuration Tuning

### For Large Repos (125k+ LOC)

Edit `chroma/mcp/chroma.py`:
```python
# Line ~80
batch_size = 10        # Reduce memory usage
```

Edit `chroma/index_repo.py`:
```python
max_files = 1000       # Increase file limit
```

### For Small Repos (<10k LOC)

```python
batch_size = 50        # Faster indexing
max_files = 100        # Standard
```

---

## Performance Optimization

### Reduce Chroma memory
```bash
# Clear old index
rm -rf chroma/.chroma

# Re-index with limits
GEMINI_API_KEY="sk-..." python chroma/index_repo.py /repo --clear
```

### Speed up queries
```python
# In mcp/server.py, reduce top_k:
results = embed_service.search(query, top_k=2)  # Instead of 5
```

### Cache embeddings
```bash
# Backup working index
cp -r chroma/.chroma chroma/.chroma.backup
```

---

## Troubleshooting

### Error: "GEMINI_API_KEY not set"
```bash
# Verify key is exported
echo $GEMINI_API_KEY

# If empty:
export GEMINI_API_KEY="sk-..."
```

### Error: "Connection refused" to localhost:8000
```bash
# Check if server is running
curl http://localhost:8000/v1/health

# If not, start it:
docker compose up
```

### Error: "Chroma initialization failed"
```bash
# Clear and rebuild
rm -rf chroma/.chroma
python index_repo.py /repo --clear
docker compose up --build
```

### Error: "Out of memory" during indexing
```bash
# Reduce batch size
Edit chroma/mcp/chroma.py:
batch_size = 5    # Very conservative

# Run indexing again
python chroma/index_repo.py /repo --clear
```

---

## Monitor Usage

### Check vector DB stats
```bash
curl http://localhost:8000/v1/health | jq
```

### View Chroma directory size
```bash
du -sh chroma/.chroma
```

### Monitor queries (if logging enabled)
```bash
docker compose logs -f mcp
```

---

## Production Deployment

### Option 1: Docker on Server
```bash
docker compose up -d
# Runs in background
```

### Option 2: Kubernetes
```bash
kubectl create deployment mcp --image=mcp-chroma:latest
kubectl expose deployment mcp --port=8000 --type=LoadBalancer
```

### Option 3: Managed Chroma
Use Chroma Cloud (when available):
- https://chroma.ai
- Drop-in replacement for local Chroma

---

## Support

For issues:
1. Check this guide
2. Review [README.md](./README.md)
3. Check Docker logs: `docker compose logs`
4. Check Chroma status: `curl http://localhost:8000/v1/health`
