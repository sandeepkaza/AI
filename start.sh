#!/usr/bin/env sh
set -eu

# Default PORT if not provided by environment (Render sets $PORT automatically)
: "${PORT:=8000}"

echo "Starting Streamlit on port ${PORT}..."

exec streamlit run streamlit_app.py \
  --server.port "${PORT}" \
  --server.address 0.0.0.0 \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --browser.gatherUsageStats false
