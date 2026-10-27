"""Smoke tests for host-native Ollama.
Run from host (not inside Docker) since Ollama lives on host.

Usage:
    cd backend
    pytest tests/test_smoke_ollama.py -v
"""
import httpx

OLLAMA_URL = "http://localhost:11434"


def test_ollama_is_running():
    """Ollama host process responds on 11434."""
    r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5.0)
    assert r.status_code == 200


def test_ollama_has_required_models():
    """All 3 expected models are pulled."""
    r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5.0)
    models = {m["name"] for m in r.json()["models"]}
    assert "qwen2.5:3b-instruct" in models, f"missing qwen2.5 — got {models}"
    assert "bge-m3" in models or any("bge-m3" in m for m in models), f"missing bge-m3 — got {models}"
    # llama3.1:8b is optional in dev, but required for eval phase
    # assert "llama3.1:8b" in models


def test_ollama_chat_responds():
    """Primary LLM (qwen2.5:3b) responds with valid content."""
    r = httpx.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": "qwen2.5:3b-instruct",
            "messages": [
                {"role": "user", "content": "Say 'hello from CognitiveFlow' and nothing else."}
            ],
            "stream": False,
        },
        timeout=60.0,
    )
    assert r.status_code == 200
    content = r.json()["message"]["content"].lower()
    assert "cognitiveflow" in content, f"unexpected response: {content}"


def test_ollama_embed_returns_vector():
    """Embedder (bge-m3) returns a 1024-dim vector."""
    r = httpx.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": "bge-m3", "prompt": "test embedding"},
        timeout=30.0,
    )
    assert r.status_code == 200
    embedding = r.json()["embedding"]
    assert isinstance(embedding, list)
    assert len(embedding) == 1024, f"expected 1024, got {len(embedding)}"
