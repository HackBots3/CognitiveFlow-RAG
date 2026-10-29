
#### Architecture Diagram (Mermaid)


```mermaid
flowchart TB
    subgraph HOST ["Windows Host (Native)"]
        Client[Browser / Next.js Client<br/>Chat UI + Doc Upload + Eval Dashboard]
        Ollama[Ollama Host-Native<br/>qwen2.5:3b-instruct + llama3.1:8b<br/>bge-m3 embeddings<br/>Direct GPU: RTX 3050]
    end
    
    Client <-->|HTTP / SSE| Backend
    Client -->|direct| Ollama
    
    subgraph DOCKER ["Docker Compose (Lean, ~1.2GB RAM)"]
        Backend[FastAPI Backend<br/>uvicorn :8000]
        Worker[Celery Worker<br/>concurrency=2]
        Redis[(Redis Stack 7.4<br/>Broker + Semantic Cache<br/>+ RediSearch)]
        Qdrant[(Qdrant 1.10<br/>Dense + Sparse Vectors)]
        Postgres[(Postgres 16<br/>Documents, Chunks,<br/>Queries, Evals)]
        
        Backend -->|enqueue task| Redis
        Redis -->|task| Worker
        Backend -->|metadata CRUD| Postgres
        Backend -->|upsert / search| Qdrant
        Worker -->|embed via host| Ollama
        Worker -->|upsert| Qdrant
        Worker -->|status update| Postgres
    end
    
    Backend <-->|LLM / Embed call| Ollama
    Backend -->|trace spans| LangfuseCloud[Langfuse Cloud<br/>50k traces/mo free]
    Backend -->|fallback web search| Tavily[Tavily API<br/>1000 free calls/mo]
    
    subgraph CLOUD ["Cloud Free Tiers (Zero Local RAM)"]
        LangfuseCloud
        Tavily
    end

    subgraph GRAPH ["LangGraph Agentic Loop (Phase 4)"]
        Router[Router / Intent Classifier]
        Router -->|direct_llm| Stream
        Router -->|vector_search| Retrieve[Hybrid Retrieve + RRF]
        Router -->|web_search| Tavily2[Tavily]
        
        Retrieve --> Rerank[Cross-Encoder Rerank<br/>bge-reranker-base]
        Rerank --> Grade[Doc Relevance Grader]
        Grade -->|irrelevant| Rewrite[Query Rewriter<br/>max 2 iterations]
        Rewrite --> Retrieve
        Grade -->|relevant| Generate[LLM Generate]
        Tavily2 --> Generate
        
        Generate --> HallucCheck[Hallucination Grader]
        HallucCheck -->|fail| Generate
        HallucCheck -->|pass| Stream[SSE Stream to Client]
    end
    
    Backend -.->|orchestrate| GRAPH
