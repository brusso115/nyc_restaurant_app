from fastapi import APIRouter
from ..models.request import MCPRequest
from ..models.response import MCPResponse
from query_api.app.services.tool_router import route_tool

router = APIRouter()

@router.post("", response_model=MCPResponse)
def mcp_controller(req: MCPRequest):
    result = route_tool(req.query, req.history, req.filters or {})
    return result