FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY scraper_worker/requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

COPY scraper_worker/ /app
COPY /common /app/common

CMD ["celery", "-A", "scraper_worker.tasks", "worker", "--loglevel=info", "--concurrency=1", "--pool=threads", "--queues=scraper_queue"]
