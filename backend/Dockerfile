FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements-heavy.txt /app/
RUN pip install --no-cache-dir -r requirements-heavy.txt

COPY backend/requirements-core.txt /app/
RUN pip install --no-cache-dir -r requirements-core.txt

# Now copy the app source code — changes here won’t bust the pip cache layer
COPY backend /app/backend

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
