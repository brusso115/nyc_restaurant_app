import os
from celery import Celery

# Get broker URL from environment or default to localhost Redis
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Initialize Celery app
app = Celery("restaurant_tasks", 
             broker=broker_url,
             include=['celery_workers.tasks'])

# Optional: Set a result backend if needed (e.g., Redis or DB)
# app.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Task routing: sends tasks to specific queues
app.conf.task_routes = {
    "celery_workers.tasks.scrape_restaurant_task": {"queue": "scraper_queue"},
    "celery_workers.tasks.embed_menu_items_task": {"queue": "embedding_queue"},
}

app.conf.broker_connection_retry_on_startup = True 
