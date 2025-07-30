from ..services.chroma_tool import get_similar_menu_items
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from ..services.chroma_tool import get_similar_menu_items
from typing import TypedDict

class ChatState(TypedDict):
    messages: list[BaseMessage]

# Function to decide whether to route to chroma search
def should_query_chroma(state):
    last_input = state['messages'][-1].content.lower()
    keywords = ['find', 'recommend', 'food', 'dish', 'menu', 'want', 'craving']
    return "use_chroma" if any(k in last_input for k in keywords) else "just_chat"

# Node for regular chat
def just_chat(state):
    llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}

# Node that queries ChromaDB
def use_chroma(state):
    query = state["messages"][-1].content
    results = get_similar_menu_items(query)
    response = AIMessage(content=results)
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