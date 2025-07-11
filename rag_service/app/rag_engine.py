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

def run_rag_pipeline(query: str, filters: dict = {}) -> dict:
    docs = get_enriched_docs(query)
    retriever = StaticRetriever(docs=docs)
    chain = build_chain(retriever)
    result = chain.invoke({"query": query})

    return result
