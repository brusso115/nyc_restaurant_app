from langchain_ollama import OllamaLLM
from .config import settings

llm = OllamaLLM(
    model=settings.ollama_model,
    temperature=0.7,
    top_p=0.9,
    top_k=40,
    num_ctx=2048,
    num_predict=500
)