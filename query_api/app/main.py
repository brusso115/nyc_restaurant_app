from fastapi import FastAPI
from query_api.app.routes import query
from query_api.app.routes import restaurants

app = FastAPI()

app.include_router(query.router, prefix="/query")
app.include_router(restaurants.router, prefix="/restaurants")