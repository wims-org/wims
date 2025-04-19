#!bash

cleanup() {
  echo "Stopping services..."
  kill $(jobs -p) 2>/dev/null
}

# Trap EXIT signal to clean up background processes
trap cleanup EXIT

if [ "$CI" = "true" ]; then
    echo "CI environment detected. Starting services with Docker Compose..."
    (docker compose -f ../docker-compose.yml -f docker-compose.tests.yml up) &
else
    (cd ../inventory/backend/src && uvicorn main:app --host 0.0.0.0 --port 5005) &
    (cd ../inventory/vue_frontend && npm run dev) &
fi

wait
