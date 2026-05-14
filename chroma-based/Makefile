.PHONY: help setup install index run test health clean docker-build docker-up docker-down

help:
	@echo "Chroma MCP Stack - Common Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup         - Full setup (install deps + index)"
	@echo "  make install       - Install Python dependencies"
	@echo "  make index         - Index repo (requires REPO_PATH)"
	@echo "  make index-clear   - Re-index repo (clear existing)"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Start MCP server locally"
	@echo "  make test          - Run test query"
	@echo "  make health        - Check server health"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker services"
	@echo "  make docker-down   - Stop Docker services"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Remove vector DB (.chroma/)"
	@echo "  make help          - Show this help"
	@echo ""
	@echo "Example:"
	@echo "  export GEMINI_API_KEY='sk-...'"
	@echo "  make setup REPO_PATH=/home/user/myproject"

setup: install index
	@echo "✅ Setup complete!"

install:
	@echo "📦 Installing dependencies..."
	pip install -q -r mcp/requirements.txt
	@echo "✅ Dependencies installed"

index:
	@echo "🔍 Indexing repository..."
	@test -n "$(REPO_PATH)" || (echo "❌ Error: REPO_PATH not set. Usage: make index REPO_PATH=/path/to/repo"; exit 1)
	python index_repo.py $(REPO_PATH)

index-clear:
	@echo "🔄 Re-indexing repository (clearing existing)..."
	@test -n "$(REPO_PATH)" || (echo "❌ Error: REPO_PATH not set. Usage: make index-clear REPO_PATH=/path/to/repo"; exit 1)
	python index_repo.py $(REPO_PATH) --clear

run:
	@echo "🚀 Starting MCP server..."
	python mcp/server.py

test:
	@echo "🧪 Running test query..."
	python mcp_tool_client.py "What is this repository about?"

health:
	@echo "🏥 Checking server health..."
	curl -s http://localhost:8000/v1/health | python -m json.tool

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t mcp-chroma:latest ./mcp

docker-up: docker-build
	@echo "🚀 Starting Docker services..."
	docker compose up -d
	@echo "✅ Services running on http://localhost:8000"

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker compose down
	@echo "✅ Services stopped"

clean:
	@echo "🧹 Cleaning up..."
	rm -rf .chroma/
	@echo "✅ Vector DB cleared"

.DEFAULT_GOAL := help
