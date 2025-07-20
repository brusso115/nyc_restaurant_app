from fastapi import FastAPI
from query_api.app.routes import mcp
from query_api.app.routes import restaurants
from query_api.app.routes import categories

app = FastAPI()

app.include_router(mcp.router, prefix="/mcp")
app.include_router(restaurants.router, prefix="/restaurants")
app.include_router(categories.router, prefix="/categories")