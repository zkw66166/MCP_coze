#!/bin/bash
# Check Status Script
# Run: ./check_status.sh

echo "=========================================="
echo "Checking Deployment Status"
echo "=========================================="
date
pwd

echo ""
echo "[1] Critical Directory Check"

for dir in "modules" "database" "config" "server"; do
    if [ -d "$dir" ]; then
        echo "✅ '$dir' exists."
    else
        echo "❌ '$dir' MISSING!"
    fi
done

echo ""
echo "[2] Process Check"
ps aux | grep -E "uvicorn|node" | grep -v grep

echo ""
echo "[3] Network Ports"
ss -tulnp | grep -E ":3000|:8000"

echo ""
echo "[4] Backend Log Tail"
if [ -f "backend.log" ]; then
    tail -n 10 backend.log
else
    echo "No backend.log found"
fi
echo "=========================================="
