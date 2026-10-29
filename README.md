# CognitiveFlow — Enterprise Self-Corrective & Adaptive Agentic Engine

> Adaptive RAG merged with an event-driven AI backend architecture. Production-grade, not a demo.

## 🎯 What Is This?

CognitiveFlow is a "ChatGPT-for-your-own-documents" app — but engineered like a production AI microservice. Users upload PDFs, ask questions, and get streamed, grounded answers with citations. Behind the scenes, it self-corrects when retrieval fails, falls back to live web search when needed, and never hallucinates without trying to fix itself.

## 🏗️ Architecture

[Embed the Mermaid diagram from §7 of this doc]

## 🧱 Tech Stack

| Layer | Tech |
|-------|------|
| LLM serving | Ollama (host-native) — qwen2.5:3b-instruct + llama3.1:8b |
| Embeddings | bge-m3 (dense + sparse in one model) |
| Reranker | bge-reranker-base (HuggingFace) |
| API | FastAPI 0.115 (Python 3.11) |
| Metadata DB | Postgres 16 |
| Vector DB | Qdrant 1.10 (native hybrid) |
| Cache + Broker | Redis Stack 7.4 |
| Workers | Celery 5.4 |
| Agentic orchestration | LangGraph 0.2+ |
| Tracing | Langfuse Cloud |
| Frontend | Next.js 14 + shadcn/ui |

## 🚀 Quickstart

### Prerequisites

- Windows 11 + WSL2 + Docker Desktop
- OR macOS / Linux with Docker
- 16GB RAM minimum (32GB recommended)
- Optional: NVIDIA GPU 4GB+ VRAM for faster inference
- Ollama installed on host: https://ollama.com

### Setup (5 minutes)

```bash
# 1. Clone
git clone https://github.com/your-team/cognitiveflow.git
cd cognitiveflow

# 2. Pull Ollama models (host-native)
bash scripts/pull_models.sh

# 3. Configure env
cp infra/.env.example infra/.env
# Edit .env and fill in:
#   - TAVILY_API_KEY  (free at https://tavily.com)
#   - LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY  (free at https://cloud.langfuse.com)

# 4. Tune WSL2 memory (Windows only)
# Create C:\Users\<You>\.wslconfig with:
#   [wsl2]
#   memory=9GB
#   processors=4
#   swap=4GB
# Then: wsl --shutdown

# 5. Boot the stack
cd infra
docker compose up -d

# 6. Initialize Qdrant collection
bash scripts/seed_qdrant.sh

# 7. Verify everything is healthy
curl http://localhost:8000/health
# All deps should report "ok"

# 8. Run smoke tests
cd backend
pytest tests/ -v
