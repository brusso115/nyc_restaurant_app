FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY embedding_worker/requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

COPY embedding_worker/ /app
COPY /common /app/common

CMD ["celery", "-A", "embedding_worker.tasks", "worker", "--loglevel=info", "--concurrency=4", "--pool=threads", "--queues=embedding_queue"]
