#!/bin/bash

set -e
set -o pipefail

cd "$(dirname "$0")"
export PYTHONPATH=$(cd .. && pwd)

echo "🔍 Checking if Redis is running..."
if ! pgrep -f redis-server > /dev/null; then
  echo "🚀 Redis not running — starting it..."
  redis-server --daemonize yes
  sleep 2
else
  echo "✅ Redis is already running"
fi

echo "🧼 Flushing Redis..."
redis-cli FLUSHALL || echo "⚠️ Failed to flush Redis"

echo "🧯 Purging Celery queues..."
celery -A scraper_worker.tasks purge -f || echo "⚠️ Failed to purge scraper queue"
celery -A embedding_worker.tasks purge -f || echo "⚠️ Failed to purge embedding queue"

echo "🔪 Killing Celery workers..."
pkill -f "celery -A scraper_worker.tasks" || echo "⚠️ No scraper workers running"
pkill -f "celery -A embedding_worker.tasks" || echo "⚠️ No embedder workers running"

echo "⛔ Stopping Redis server..."
pkill -f redis-server || echo "⚠️ Redis not running"

echo "✅ Cleanup complete."
