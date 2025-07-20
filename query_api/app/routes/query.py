from fastapi import APIRouter
from ..models.request import QueryRequest
from ..models.response import QueryResponse
from ..services.rag_wrapper import query_rag

router = APIRouter()

@router.post("", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    result = query_rag(query=request.query, filters=request.filters or {}, history=request.history or [])
    print(result)
    return result