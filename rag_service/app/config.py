from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    chroma_path: str = "./chroma_db"
    model_name: str = "./embedding_worker/sentence_transformer_model"
    ollama_model: str = "mistral"

settings = Settings()