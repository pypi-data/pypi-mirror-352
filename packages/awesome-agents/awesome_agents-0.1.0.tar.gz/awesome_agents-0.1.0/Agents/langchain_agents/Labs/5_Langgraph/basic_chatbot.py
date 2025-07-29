from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from agentsapi.utils.utils import init

init()


# State
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Graph Builder
graph_builder = StateGraph(State)

from langchain_openai import OpenAI

llm = OpenAI()


# print(llm.invoke("welcome"))

# def chatbot(state: State):
#     return {"messages": [llm.invoke(state["messages"])]}
def chatbot(state: State):
    user_messages = state["messages"]
    response = llm.invoke(user_messages)
    return {"messages": user_messages + [{"role": "assistant", "content": response}]}


graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

print(graph)


# def stream_graph_updates(user_input:str):
#     for event in graph.stream({"messages":[{"role":"user","content":user_input}]}):
#         for value in event.values():
#             #print("Assistant",value["messages"][-1])
#             print("Assistant:", value["messages"][-1].content)

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print(type(value["messages"][-1]))
            #print("Assistant:", str(value["messages"][-1].content))
            print("Assistant:", value["messages"][-1]["content"])
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break