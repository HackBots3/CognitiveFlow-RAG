# ADR-001: Technology Stack & Infrastructure Topology for CognitiveFlow


## Context

CognitiveFlow requires a stack that:
1. Runs 100% locally (no OpenAI/Anthropic API spend)
2. Supports hybrid vector search (dense + sparse)
3. Provides agentic state-machine orchestration (cycles, not just chains)
4. Has first-class observability
5. Runs smoothly on a dev laptop with 4GB VRAM + 16GB RAM (Windows/WSL2)

## Decision

### Models

| Role | Chosen | Rationale |
|------|--------|-----------|
| Primary LLM | `qwen2.5:3b-instruct` | 2.2GB footprint fits 100% in 4GB VRAM → 35+ tok/s, no GPU/CPU split thrash |
| Heavy reasoning LLM | `llama3.1:8b` (on-demand) | Used only for final generation + eval suite where output quality matters |
| Embeddings | `bge-m3` | Produces dense + sparse + multi-vector in ONE call. Free, no API dependency |
| Reranker | `bge-reranker-base` (HuggingFace) | CPU-runnable, free, 510MB |

### Infrastructure Topology — Hybrid (Host + Docker + Cloud)

| Layer | Chosen | Rationale |
|-------|--------|-----------|
| LLM serving | **Ollama host-native** (NOT in Docker) | Direct GPU passthrough, zero WSL2 VM overhead. Mirrors production pattern where inference runs on dedicated compute (vLLM/Triton), decoupled from app layer |
| API | FastAPI 0.115 | Async, OpenAPI docs free, SSE-native |
| Metadata DB | Postgres 16 Alpine | Lightweight image (~80MB) |
| Vector DB | Qdrant 1.10 | Native hybrid (dense + sparse) in one collection |
| Cache + Broker | Redis Stack 7.4 (server-only) | Smaller image, RediSearch module enables semantic cache later |
| Workers | Celery 5.4 | Survives worker crashes via Redis persistence |
| Agentic orchestration | LangGraph 0.2+ | Cyclic state machine — that's what makes this "agentic" not "chain" |
| Tracing | **Langfuse Cloud free tier** | Zero ops burden, 50k traces/mo, same SDK as self-host. Saves ~2GB local RAM |
| Web search fallback | Tavily API free tier | 1000 calls/mo is enough for dev/demo |
| Frontend | Next.js 14 + shadcn/ui | Vercel AI SDK handles SSE chat for free |

## Consequences

**Positive:**
- Zero recurring API cost — entire stack runs on one laptop
- ~1.2GB RAM idle for Docker stack + ~3GB for Ollama = ~4.2GB total. Leaves 11GB for Windows + IDE + browser
- 35+ tok/s inference speed on qwen2.5:3b — fast enough for live demo
- Every architectural choice defensible in interview (see "Defense" section below)

**Negative:**
- Hybrid topology (host + Docker) means teammates must install Ollama on their own host OS — slightly less reproducible than "everything in Docker"
- Langfuse Cloud free tier rate-limits at 50k traces/mo — sufficient for dev, but would need self-hosting at production scale
- qwen2.5:3b is weaker than llama3.1:8b on complex reasoning — requires swapping models contextually (3b for routing/grader, 8b for final answer)

## Defense — How to Explain This in Interviews

**Q: "Why is Ollama on the host instead of in Docker?"**
A: "In production, LLM inference runs on dedicated compute clusters (vLLM on Kubernetes, Triton Inference Server, or managed endpoints), decoupled from the application and ingestion layer. We mirrored that decoupling by isolating state, search, and background workers in Docker, while serving the model from a separate endpoint with direct GPU passthrough — exactly how a real ML platform team would partition concerns."

**Q: "Why Langfuse Cloud and not self-hosted?"**
A: "Self-hosting Langfuse requires 3 containers (web, worker, ClickHouse) consuming ~2GB RAM idling — a non-trivial cost on a 16GB dev machine. The cloud free tier gives us the same SDK, the same UI, and 50k traces/mo with zero ops burden. In production we'd self-host for data residency, but for dev the cloud tier removes a major source of friction."

**Q: "Why qwen2.5:3b instead of llama3.1:8b?"**
A: "3B fits entirely in 4GB VRAM and runs at 35+ tok/s, while 8B requires GPU/CPU split-layer inference that thrashes memory and drops to 4-7 tok/s. We use 3B for high-frequency tasks (intent routing, doc relevance grading, hallucination checks) and 8B only for the final user-facing answer where output quality matters most. This is the same 'small model for routing, large model for generation' pattern used by GPT-4 + GPT-3.5 routing in production chatbots."

## Revisit Triggers

- If we add multi-tenancy → re-evaluate Postgres vs. dedicated vector DB separation
- If we hit >50 RPS → re-evaluate Celery vs. alternative async patterns
- If Ollama proves too slow for demo even with qwen2.5:3b → switch to Groq API (free, fast inference)
- If Langfuse Cloud rate-limits us → switch to self-hosted Langfuse on a separate machine
