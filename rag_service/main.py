from app.rag_engine import run_rag_pipeline

if __name__ == "__main__":
    query = "I'm looking for some spicy vegan options"
    result = run_rag_pipeline(query)
    print("\nAnswer:\n", result["result"])
    print("\nSource Documents:")
    for doc in result["source_documents"]:
        print("-", doc.page_content)