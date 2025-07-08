FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY scraper/requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

RUN playwright install --with-deps

COPY scraper/ /app
COPY common/ /app/common

CMD ["python", "postmates_link_scraper.py"]
