from pydantic import BaseModel

class RestaurantResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    categories: list

class CategoryResponse(BaseModel):
    name: str