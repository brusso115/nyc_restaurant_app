from fastapi import APIRouter
from ..models.response import RestaurantResponse
from typing import List
from query_api.app.db.api_db import RestaurantAPIData

router = APIRouter()

@router.get("", response_model=List[RestaurantResponse])
def get_restaurants():
    db = RestaurantAPIData()
    try:
        return db.fetch_all_restaurants()
    finally:
        db.close()