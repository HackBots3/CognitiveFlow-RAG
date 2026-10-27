"""Smoke test for Qdrant collection schema."""
from qdrant_client import QdrantClient

QDRANT_URL = "http://localhost:6333"
COLLECTION = "docs"


def test_qdrant_collection_exists():
    """The 'docs' collection was created by seed_qdrant.sh."""
    client = QdrantClient(url=QDRANT_URL)
    collections = client.get_collections().collections
    names = {c.name for c in collections}
    assert COLLECTION in names, f"missing '{COLLECTION}' — run scripts/seed_qdrant.sh"


def test_qdrant_collection_has_hybrid_schema():
    """Collection has BOTH dense (vector) AND sparse vectors configured."""
    client = QdrantClient(url=QDRANT_URL)
    info = client.get_collection(COLLECTION)
    
    # Dense vector config
    assert info.config.params.vectors is not None, "no dense vectors configured"
    
    # Sparse vector config
    sparse = info.config.params.sparse_vectors
    assert sparse is not None, "no sparse vectors configured"
    assert "sparse" in sparse, f"expected 'sparse' key, got {list(sparse.keys())}"
