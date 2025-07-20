from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .llm import llm

prompt_template = PromptTemplate(
    input_variables=["query", "context", "chat_history"],
    template="""
You are a helpful assistant recommending menu items from New York City restaurants.

Each item includes the restaurant name and address. Use this info to help the user decide what to eat. Based on the restaurant's name or location, feel free to infer what kind of place it is (e.g., casual, upscale, fast food, trendy).

Here is the conversation so far:
{chat_history}

Menu Items:
{context}

Question: {query}
Answer:
"""
)

def build_chain():
    return LLMChain(llm=llm, prompt=prompt_template)
