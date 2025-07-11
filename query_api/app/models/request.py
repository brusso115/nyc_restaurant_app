from pydantic import BaseModel
from typing import Optional, Dict

class QueryRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, float]] = None