from rag_service.app.rag_engine import run_rag_pipeline

def query_rag(query: str, filters: dict, history: list) -> dict:
    result = run_rag_pipeline(query=query, filters=filters, history=history)

    return result
