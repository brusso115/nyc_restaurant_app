#!/bin/bash

set -e
set -o pipefail

# Go to the folder this script lives in
cd "$(dirname "$0")"
export PYTHONPATH=$(cd .. && pwd)

# Activate the virtualenv (sibling folder)
# source ../restaurant-recommender-env/bin/activate

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

echo "🧯 Purging all Celery queues..."
celery -A celery_workers.celery_app purge -f || echo "⚠️ Failed to purge Celery queues"

echo "🔪 Killing all Celery workers..."
pkill -f "celery -A celery_workers.celery_app" || echo "⚠️ No Celery workers found"

echo "⛔ Stopping Redis server..."
pkill -f redis-server || echo "⚠️ Redis server may not have been running"

echo "✅ Cleanup complete."
