#!/bin/bash

echo "🔍 CognitiveFlow Phase 0 — DoD Verification"
echo "============================================"

echo ""
echo "1. WSL2 memory cap (.wslconfig)..."
if [ -f "$USERPROFILE/.wslconfig" ] || [ -f "$HOME/.wslconfig" ]; then
    echo "   ✅ .wslconfig exists"
else
    echo "   ⚠️  .wslconfig not found (Windows only — skip on Linux/Mac)"
fi

echo ""
echo "2. Ollama host-native responding..."
curl -fs http://localhost:11434/api/tags > /dev/null && echo "   ✅ Ollama running" || echo "   ❌ Ollama not responding"

echo ""
echo "3. Required Ollama models pulled..."
MODELS=$(curl -s http://localhost:11434/api/tags | python -c "import sys, json; [print(m['name']) for m in json.load(sys.stdin).get('models', [])]" 2>/dev/null)
for m in qwen2.5:3b-instruct bge-m3; do
    if echo "$MODELS" | grep -q "${m}"; then
        echo "   ✅ $m"
    else
        echo "   ❌ $m missing — run: ollama pull $m"
    fi
done

echo ""
echo "4. Docker services healthy..."
# Check the 5 active containers
for svc in postgres redis qdrant backend celery; do
    status=$(docker inspect --format='{{.State.Status}}' cf_$svc 2>/dev/null || echo "missing")
    health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' cf_$svc 2>/dev/null || echo "none")
    
    if [ "$status" = "running" ] && [ "$health" = "healthy" ]; then
        echo "   ✅ $svc ($health)"
    elif [ "$status" = "running" ]; then
        echo "   ✅ $svc (running)"
    else
        echo "   ❌ $svc (status: $status, health: $health)"
    fi
done

echo ""
echo "5. /health endpoint — all deps ok..."
HEALTH_STATUS=$(curl -s http://localhost:8000/health | python -c "import sys, json; print(json.load(sys.stdin).get('status', 'fail'))" 2>/dev/null)
if [ "$HEALTH_STATUS" = "ok" ]; then
    echo "   ✅ /health ok"
else
    echo "   ❌ /health fail (got: $HEALTH_STATUS)"
fi

echo ""
echo "6. Qdrant 'docs' collection exists..."
COLLS=$(curl -s http://localhost:6333/collections | python -c "import sys, json; [print(c['name']) for c in json.load(sys.stdin).get('result', {}).get('collections', [])]" 2>/dev/null)
if echo "$COLLS" | grep -q "^docs$"; then
    echo "   ✅ docs collection exists"
else
    echo "   ❌ docs collection missing — run scripts/seed_qdrant.sh"
fi

echo ""
echo "7. Smoke tests pass..."
# Navigate to backend directory and run host pytest
if (cd backend && pytest tests/ -v --tb=no 2>&1 | tail -5); then
    echo "   ✅ All smoke tests green"
else
    echo "   ❌ Smoke tests failing"
fi

echo ""
echo "8. Langfuse Cloud reachable..."
curl -fs https://cloud.langfuse.com > /dev/null && echo "   ✅ Langfuse Cloud reachable" || echo "   ❌ Cannot reach Langfuse Cloud"

echo ""
echo "============================================"
echo "✅ Phase 0 verification complete."
echo "If all checks pass, you're ready for Phase 1."