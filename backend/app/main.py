from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import redis.asyncio as aioredis
from qdrant_client import QdrantClient

from app.config import settings


# Module-level clients (created at startup, reused across requests)
pg_engine = None
redis_client = None
qdrant_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pg_engine, redis_client, qdrant_client
    
    # Startup
    print(f"🚀 {settings.app_name} starting in {settings.app_env} mode")
    
    pg_engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=5)
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    qdrant_client = QdrantClient(url=settings.qdrant_url)
    
    yield
    
    # Shutdown
    await pg_engine.dispose()
    await redis_client.close()
    qdrant_client.close()
    print(f"👋 {settings.app_name} shutting down")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Comprehensive health check — verifies all 4 dependencies."""
    checks = {"service": settings.app_name, "env": settings.app_env}
    
    # 1. Postgres
    try:
        async with pg_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"fail: {e.__class__.__name__}"
    
    # 2. Redis
    try:
        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"fail: {e.__class__.__name__}"
    
    # 3. Qdrant
    try:
        qdrant_client.get_collections()
        checks["qdrant"] = "ok"
    except Exception as e:
        checks["qdrant"] = f"fail: {e.__class__.__name__}"
    
    # 4. Ollama (host-native)
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.get(f"{settings.ollama_url}/api/tags")
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
        checks["ollama"] = f"ok ({len(models)} models)"
    except Exception as e:
        checks["ollama"] = f"fail: {e.__class__.__name__}"
    
    # Overall status
    all_ok = all(v == "ok" or v.startswith("ok") for k, v in checks.items() 
                if k not in ("service", "env"))
    checks["status"] = "ok" if all_ok else "degraded"
    
    return checks
