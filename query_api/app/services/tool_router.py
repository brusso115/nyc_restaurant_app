from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_community.chat_models import ChatOllama
from query_api.app.services.tools.rag_wrapper import query_rag
from typing import List, Dict
from query_api.app.models.request import QueryTurn

# LangChain-compatible tool wrapper
def rag_wrapper(query: str, history: List[QueryTurn]) -> str:
    result = query_rag(query, filters={}, history=history)
    return result["answer"]

# Define tool metadata
tools = [
    Tool(
        name="run_rag",
        func=lambda query: rag_wrapper(query, []),
        description="Answer open-ended user questions about what to eat using restaurant menu data."
    ),
    # Add more tools here
]

# Use local Mistral via Ollama
llm = ChatOllama(base_url="http://host.docker.internal:11434", model="mistral")

# Initialize agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Entry point
def route_tool(query: str, history: List[QueryTurn], filters: Dict = {}) -> dict:
    answer = agent.run(query)
    return {
        "answer": answer,
        "sources": [],
        "tool_used": "run_rag",
        "history": history + [{"query": query, "response": answer, "sources": []}]
    }
