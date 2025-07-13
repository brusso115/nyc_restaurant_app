FROM python:3.10-slim

WORKDIR /app

COPY query_api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY query_api /app/query_api
COPY rag_service /app/rag_service

EXPOSE 8000

CMD ["uvicorn", "query_api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
