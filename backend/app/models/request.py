from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    history: list[dict]  # list of {"role": "user"/"assistant", "content": "..."}