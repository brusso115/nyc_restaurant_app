from fastapi import FastAPI
from backend.app.routes import restaurants
from backend.app.routes import categories
from backend.app.routes import chat

app = FastAPI()

app.include_router(chat.router, prefix="/chat")
app.include_router(restaurants.router, prefix="/restaurants")
app.include_router(categories.router, prefix="/categories")