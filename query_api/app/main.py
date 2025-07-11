from fastapi import FastAPI
from query_api.app.routes import query

app = FastAPI()

app.include_router(query.router, prefix="/query")