from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.llm import llm

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

def build_chain(retriever) -> RetrievalQA:
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=True
    )
