from fastapi import FastAPI
from query_api.app.routes import query
from query_api.app.routes import restaurants
from query_api.app.routes import categories

app = FastAPI()

app.include_router(query.router, prefix="/query")
app.include_router(restaurants.router, prefix="/restaurants")
app.include_router(categories.router, prefix="/categories")