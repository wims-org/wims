#/bin/bash

cleanup() {
  echo "Stopping services..."
  kill $(jobs -p) 2>/dev/null
}

# Trap EXIT signal to clean up background processes
trap cleanup EXIT

# run in Docker:
if [ "$CI" = "true" ] || [ "$CONTAINERIZED" = "true" ]; then
    # Check if frontend is reachable
    echo "Container mode."
else
    # or run native:
    echo "Native mode."
    (cd ../backend/src && uv run uvicorn main:app --host 0.0.0.0 --port 5005) &
    (cd ../vue_frontend && npm run dev) &
fi 

wait
