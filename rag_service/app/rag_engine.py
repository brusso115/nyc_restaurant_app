from .retriever import get_enriched_docs
from .chain import build_chain
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from typing import Optional, List
from pydantic import Field

class StaticRetriever(BaseRetriever):
    docs: List[Document] = Field(...)

    def _get_relevant_documents(
        self, query: str, *, config: Optional[dict] = None
    ) -> List[Document]:
        return self.docs

def run_rag_pipeline(query: str, filters: dict = {}, history: list = []) -> dict:
    docs = get_enriched_docs(query)

    chat_history_text = ""

    for turn in history:
        chat_history_text += f"User: {turn.query}\nBot: {turn.response}\n"

    chain = build_chain()

    result = chain.invoke({
        "query": query,
        "chat_history": chat_history_text.strip(),
        "context": "\n".join([doc.page_content for doc in docs])
    })

    return {
        "answer": result['text'], 
        "sources": [doc.metadata["restaurant_name"] for doc in docs]
    }

