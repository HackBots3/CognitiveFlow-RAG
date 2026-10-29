from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for resolving .env files reliably
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", BASE_DIR.parent / "infra" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "CognitiveFlow"
    app_env: str = "development"
    log_level: str = "INFO"

    # Postgres
    database_url: str = "postgresql+asyncpg://cognitive:cognitive@localhost:5432/cognitiveflow"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "docs"

    # Ollama (host-native)
    ollama_url: str = "http://host.docker.internal:11434"
    ollama_llm_model: str = "qwen2.5:3b-instruct"          # PRIMARY — fast
    ollama_llm_model_heavy: str = "llama3.1:8b"            # HEAVY — for final answer
    ollama_embed_model: str = "bge-m3"
    ollama_llm_temperature: float = 0.1
    ollama_llm_max_tokens: int = 2048

    # Reranker
    reranker_model: str = "BAAI/bge-reranker-base"

    # Tavily
    tavily_api_key: str = ""

    # Langfuse (Cloud / Self-host)
    langfuse_host: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None

    # Cache
    cache_similarity_threshold: float = 0.92
    cache_ttl_seconds: int = 86400

    # Retrieval
    retrieval_top_k_dense: int = 20
    retrieval_top_k_sparse: int = 20
    rerank_top_k: int = 4
    rrf_k: int = 60

    # Graph
    query_rewrite_max_iter: int = 2
    hallucination_threshold: float = 0.7

    # Storage
    upload_dir: str = "/app/uploads"
    chunk_size: int = 1000
    chunk_overlap: int = 200


settings = Settings()