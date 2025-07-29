from typing_extensions import TypedDict


class State(TypedDict):
    graph_state: str


# print(State)

def first_node(state):
    print("my first Node is called")
    return {"graph_state": state["graph_state"] + "I am Playing"}


def second_node(state):
    print("My Second Node is called")
    return {"graph_state": state["graph_state"] + "Cricket"}


def third_node(state):
    print("My 3rd Node is called")
    return {"graph_state": state["graph_state"] + "Badminton"}


import random
from typing import Literal


def decide_play(state) -> Literal["second_node", "third_node"]:
    graph_state = state["graph_state"]

    if random.random() < 0.5:
        return "second_node"
    return "third_node"


# Graph

from langgraph.graph import StateGraph, START, END

## Build Graph
builder = StateGraph(State)
builder.add_node("first_node", first_node)
builder.add_node("second_node", second_node)
builder.add_node("third_node", third_node)

## Logic
builder.add_edge(START, "first_node")
builder.add_conditional_edges("first_node", decide_play)
builder.add_edge("second_node", END)
builder.add_edge("third_node", END)

## Add

graph = builder.compile()

## View
# display(Image(graph.get_graph()))


ress = graph.invoke({"graph_state": "Hi ,my name is abc"})
print(ress)
