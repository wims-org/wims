#/bin/bash

cleanup() {
  echo "Stopping services..."
  kill $(jobs -p) 2>/dev/null
}

# Trap EXIT signal to clean up background processes
trap cleanup EXIT

# run in Docker:
if [ "$CI" = "true" ]; then
    echo "CI environment detected. Starting services with Docker Compose..."
    (docker compose -f ../docker-compose.yml -f docker-compose.tests.yml up --build) &
else

# or run native:
    (cd ../backend/src && poetry run uvicorn main:app --host 0.0.0.0 --port 5005) &
    (cd ../vue_frontend && npm run dev) &
fi 

wait
