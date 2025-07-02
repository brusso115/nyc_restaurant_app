#!/bin/bash

set -e
set -o pipefail

# Set PYTHONPATH to project root so all modules work
export PYTHONPATH=$(cd "$(dirname "$0")/.." && pwd)

# Cleanup on exit
cleanup() {
  echo "🧹 Cleaning up..."
  echo "⛔ Killing Redis..."
  pkill -f redis-server || true

  echo "⛔ Killing Celery workers..."
  pkill -f "celery -A scraper_worker.tasks" || true
  pkill -f "celery -A embedding_worker.tasks" || true

  # Optional: wait a bit to let Redis or Celery shut down gracefully
  sleep 1
}

trap cleanup SIGINT SIGTERM EXIT

# Start Redis
echo "🚀 Starting Redis..."
redis-server > /dev/null 2>&1 &
sleep 2

# Start Scraper Worker
echo "🕷️ Starting Scraper Worker..."
celery -A scraper_worker.tasks worker \
  --loglevel=info \
  --concurrency=1 \
  --pool=threads \
  --queues=scraper_queue \
  --hostname=scraper_worker@%h &
SCRAPER_PID=$!

# Start Embedder Worker
echo "🧠 Starting Embedder Worker..."
celery -A embedding_worker.tasks worker \
  --loglevel=info \
  --concurrency=4 \
  --pool=threads \
  --queues=embedding_queue \
  --hostname=embedding_worker@%h &
EMBEDDER_PID=$!

# Optional: Run your scraper to enqueue jobs
echo "🔍 Running scraper..."
python ../scraper/postmates_link_scraper.py

# Keep script alive until workers terminate
wait $SCRAPER_PID
wait $EMBEDDER_PID
