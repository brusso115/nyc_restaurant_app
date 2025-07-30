from ..models.request import ChatRequest
from fastapi import APIRouter
from pydantic import BaseModel
from ..services.rag_graph import compiled_graph
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter()

@router.post("")
def chat(req: ChatRequest):
    messages = []

    for msg in req.history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=req.query))

    result = compiled_graph.invoke({"messages": messages})
    response = result["messages"][-1].content

    return {"response": response}