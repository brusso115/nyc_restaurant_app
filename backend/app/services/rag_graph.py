from ..services.chroma_tool import get_similar_menu_items
from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.messages import SystemMessage
from ..services.chroma_tool import get_similar_menu_items
from typing import TypedDict
import os

class ChatState(TypedDict):
    messages: list[BaseMessage]

# Function to decide whether to route to chroma search
def should_query_chroma(state):
    last_input = state['messages'][-1].content.lower()
    keywords = ['find', 'recommend', 'food', 'dish', 'menu', 'want', 'craving']
    return "use_chroma" if any(k in last_input for k in keywords) else "just_chat"

# Node for regular chat
def just_chat(state):
    llm = ChatOpenAI(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        base_url="https://api.together.xyz/v1",
        api_key=os.getenv("TOGETHER_API_KEY"),
        temperature=0.3
    )
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}

# Node that queries ChromaDB
def use_chroma(state):
    query = state["messages"][-1].content
    menu_matches = get_similar_menu_items(query)

    print(menu_matches)

    llm = ChatOpenAI(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        base_url="https://api.together.xyz/v1",
        api_key=os.getenv("TOGETHER_API_KEY"),
        temperature=0.3
    )

    system_prompt = SystemMessage(
        content=(
            "You are a friendly restaurant assistant. Based on the user's craving and a list of matching menu items, "
            "recommend dishes from the **given list only**. Do not make up dishes or restaurants not found in the list. "
            "Respond in a natural, conversational tone. Include the restaurant name and address from the provided items. "
            "Do not list the raw menu items — instead, rewrite them as recommendations."
        )
    )

    assistant_context = AIMessage(
        content=f"The following menu items were retrieved based on the user's query:\n{menu_matches}"
    )

    messages = [
        system_prompt,
        HumanMessage(content=query),
        assistant_context
    ]

    response = llm.invoke(messages)

    return {"messages": state["messages"] + [response]}

# Identity router node (to enable branching)
def router(state):
    return state

# Build LangGraph flow
graph = StateGraph(ChatState)

graph.add_node("router", router)
graph.add_node("just_chat", just_chat)
graph.add_node("use_chroma", use_chroma)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    should_query_chroma,
    {
        "just_chat": "just_chat",
        "use_chroma": "use_chroma"
    }
)

graph.add_edge("just_chat", END)
graph.add_edge("use_chroma", END)

compiled_graph = graph.compile()