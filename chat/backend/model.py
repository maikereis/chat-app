from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

MODEL = "qwen2.5:7b"


class ChatState(TypedDict):
    messages: list[str]
    session_id: str


def agent_node(state: ChatState):
    model = ChatOllama(
        model=MODEL,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Você é um útil assistente!",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    generate = prompt | model

    ai_msg = generate.invoke(state["messages"])

    return {"messages": [ai_msg]}


workflow = StateGraph(ChatState)
workflow.add_node("model", agent_node)
workflow.add_edge(START, "model")
workflow.add_edge("model", END)
agent = workflow.compile()
