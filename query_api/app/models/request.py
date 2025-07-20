from pydantic import BaseModel
from typing import Optional, Dict, List

class QueryTurn(BaseModel):
    query: str
    response: str
    sources: Optional[List[str]] = []

class MCPRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, float]] = None
    history: Optional[List[QueryTurn]] = []