#!/bin/sh
set -eu

STREAMLIT_INTERNAL_PORT="${STREAMLIT_SERVER_PORT:-8501}"
RAILWAY_PORT="${PORT:-8080}"

sed -i "s/listen 8080;/listen ${RAILWAY_PORT};/" /etc/nginx/nginx.conf

streamlit run app.py \
  --server.port="${STREAMLIT_INTERNAL_PORT}" \
  --server.address=127.0.0.1 \
  &

STREAMLIT_PID=$!

cleanup() {
  kill -TERM "$STREAMLIT_PID" 2>/dev/null || true
  wait "$STREAMLIT_PID" 2>/dev/null || true
}

trap cleanup INT TERM

nginx -g "daemon off;"
