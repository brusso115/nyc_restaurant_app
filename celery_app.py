import os
from celery import Celery

# Get broker URL from environment or default to localhost Redis
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Initialize Celery app
app = Celery("restaurant_tasks", 
             broker=broker_url,
             include=['tasks'])

# Optional: Set a result backend if needed (e.g., Redis or DB)
# app.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Task routing: sends tasks to specific queues
app.conf.task_routes = {
    "tasks.scrape_restaurant_task": {"queue": "scraper_queue"},
    "tasks.embed_menu_items_task": {"queue": "embedding_queue"},
}
