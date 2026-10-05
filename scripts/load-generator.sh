#!/usr/bin/env bash
# Generate order traffic. Usage: load-generator.sh [count] [base_url]
set -euo pipefail
COUNT="${1:-50}"
URL="${2:-http://localhost:8080}"
for i in $(seq 1 "$COUNT"); do
  qty=$(( RANDOM % 5 + 1 ))
  price=$(( RANDOM % 90 + 10 ))
  curl -s -o /dev/null -w "%{http_code}\n" -X POST "$URL/orders" \
    -H 'Content-Type: application/json' \
    -d "{\"customer\":\"user$((RANDOM % 20))\",\"item\":\"widget\",\"quantity\":$qty,\"unitPrice\":$price}"
  sleep 0.2
done
