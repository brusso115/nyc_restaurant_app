from celery import Celery

app = Celery(
    "restaurant_recommender",
    broker="redis://localhost:6379/0",   
    backend="redis://localhost:6379/0",
    include=['tasks']
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_concurrency = 1
)