from pydantic import BaseModel
from typing import List

class QueryTurn(BaseModel):
    query: str
    response: str
    sources: List[str]

class MCPResponse(BaseModel):
    answer: str
    sources: List[str]
    history: List[QueryTurn]

class RestaurantResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    categories: list

class CategoryResponse(BaseModel):
    name: str