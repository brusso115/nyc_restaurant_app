from fastapi import APIRouter, Depends
from typing import List
from ..models.response import CategoryResponse
from query_api.app.db.api_db import RestaurantAPIData

router = APIRouter()

@router.get("", response_model=List[CategoryResponse])
def get_categories():
    
    db = RestaurantAPIData()
    try:
        return db.fetch_all_categories()
    finally:
        db.close()