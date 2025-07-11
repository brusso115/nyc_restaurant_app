from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from .config import settings

embedding_model = HuggingFaceEmbeddings(model_name=settings.model_name)
vectorstore = Chroma(
    collection_name="menu_items",
    persist_directory=settings.chroma_path,
    embedding_function=embedding_model
)

def get_enriched_docs(query: str, k: int = 3) -> list[Document]:
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)

    print(f"Retrieved {len(docs)} documents for query: '{query}'")

    for doc in docs:
        name = doc.metadata.get("restaurant_name", "Unknown")
        address = doc.metadata.get("restaurant_address", "Unknown")
        doc.page_content = f"{doc.page_content} — from {name} ({address})"
    return docs
