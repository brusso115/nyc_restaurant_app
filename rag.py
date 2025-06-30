from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from typing import List, Optional

# Load the same embedding model used during indexing
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Connect to the vector DB (Chroma) and access the right collection
vectorstore = Chroma(
    collection_name="menu_items",
    persist_directory="chroma_db",
    embedding_function=embedding_model
)

# Prompt that encourages the LLM to reason about the restaurant and location
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant recommending menu items from New York City restaurants.

Each item includes the restaurant name and address. Use this info to help the user decide what to eat. Based on the restaurant's name or location, feel free to infer what kind of place it is (e.g., casual, upscale, fast food, trendy).

Menu Items:
{context}

Question: {question}
Answer:
"""
)

# Configure the local LLM (via Ollama). This one uses the Mistral model.
llm = OllamaLLM(
    model="mistral",
    temperature=0.7,
    top_p=0.9,
    top_k=40,
    num_ctx=2048,
    num_predict=500
)

# Run a vector search for a user query
query = "I'm looking for menu items that are keto friendly"
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
docs = retriever.invoke(query)

# Add restaurant name and address to each menu item before passing to the LLM
for doc in docs:
    name = doc.metadata.get("restaurant_name", "Unknown Restaurant")
    address = doc.metadata.get("restaurant_address", "Unknown Address")
    doc.page_content = f"{doc.page_content} — from {name} ({address})"

# Create a static retriever that just returns these enriched documents
class StaticRetriever(BaseRetriever):
    def _get_relevant_documents(self, query: str, *, config: Optional[dict] = None) -> List[Document]:
        return docs

# Pass everything into the RAG pipeline
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=StaticRetriever(),
    chain_type_kwargs={"prompt": prompt_template},
    return_source_documents=True
)

# Run the full query-response chain
result = qa_chain.invoke({"query": query})

# Show the final answer from the model
print("\n💬 Answer:\n", result["result"])

# Show which documents were actually passed in as context
print("\n📚 Source Documents:")
for doc in result["source_documents"]:
    print("-", doc.page_content)