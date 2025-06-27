#!/bin/bash

set -e
set -o pipefail

# Cleanup function to kill background jobs on exit
cleanup() {
  echo "🧹 Cleaning up..."
  echo "⛔ Killing Redis..."
  pkill -f redis-server || true
  echo "⛔ Killing all Celery workers..."
  pkill -f "celery -A celery_app" || true
  exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Optional: activate virtualenv
# source restaurant-recommender-env/bin/activate

# Start Redis
echo "🚀 Starting Redis..."
redis-server > /dev/null 2>&1 &
sleep 2

# Start Celery embedding worker
echo "📦 Starting Celery embedding worker..."
celery -A celery_app worker --loglevel=info --concurrency=8 --pool=threads --queues=embedding_queue &
EMBED_PID=$!

# Start Celery scraper worker
echo "🕸️ Starting Celery scraper worker..."
celery -A celery_app worker --loglevel=info --concurrency=1 --pool=threads --queues=scraper_queue &
SCRAPER_PID=$!

# Wait a bit
sleep 3

# Run the scraper
# echo "🔍 Running scraper..."
python postmates_link_scraper.py

# Wait for workers to finish (keeps script open until killed)
wait $EMBED_PID
wait $SCRAPER_PID