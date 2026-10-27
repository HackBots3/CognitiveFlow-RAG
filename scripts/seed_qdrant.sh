#!/bin/bash
set -e

QDRANT=${QDRANT_URL:-http://localhost:6333}
COLLECTION=${QDRANT_COLLECTION:-docs}

echo "📦 Creating Qdrant collection: $COLLECTION (hybrid: dense + sparse)"

curl -sS -X PUT "$QDRANT/collections/$COLLECTION" \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "dense": {"size": 1024, "distance": "Cosine"}
    },
    "sparse_vectors": {
      "sparse": {}
    }
  }' 

echo ""
echo "📋 Collections:"
curl -sS "$QDRANT/collections"

echo ""
echo "🔍 Collection info:"
curl -sS "$QDRANT/collections/$COLLECTION"
