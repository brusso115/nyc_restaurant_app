from pydantic import BaseModel
from typing import List

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

class RestaurantResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float