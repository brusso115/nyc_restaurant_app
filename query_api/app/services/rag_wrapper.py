from rag_service.app.rag_engine import run_rag_pipeline

def query_rag(query: str, filters: dict) -> dict:
    result = run_rag_pipeline(query=query, filters=filters)
    print(result)
    return {
        "answer": result["result"],
        "sources": [doc.page_content for doc in result.get("source_documents", [])]
    }