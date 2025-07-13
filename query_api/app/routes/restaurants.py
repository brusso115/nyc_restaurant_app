from fastapi import APIRouter
from ..models.response import RestaurantResponse
from typing import List

router = APIRouter()

@router.get("", response_model=List[RestaurantResponse])
def get_all_restaurants():
    
    return [
        {
            "id": 1,
            "name": "Cafe Mogador",
            "latitude": 40.7295,
            "longitude": -73.9846
        },
        {
            "id": 2,
            "name": "Superiority Burger",
            "latitude": 40.728,
            "longitude": -73.987
        }
    ]