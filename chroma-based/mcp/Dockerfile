FROM python:3.11-slim

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# app
COPY server.py /app/server.py
COPY repo_indexer.py /app/repo_indexer.py
COPY chroma.py /app/chroma.py

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
