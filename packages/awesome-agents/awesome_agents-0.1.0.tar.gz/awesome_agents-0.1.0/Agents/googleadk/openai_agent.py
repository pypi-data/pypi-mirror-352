import os
import random

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

model = LiteLlm(
    model="openai/gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)


def get_dad_joke():
    jokes = [
        "Why did the chicken cross the road? To get to the other side!",
        "What do you call a belt made of watches? A waist of time.",
        "What do you call fake spaghetti? An impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
    ]
    return random.choice(jokes)


root_agent = Agent(
    name="openai_dad_joke_agent",
    model=model,
    description="Dad joke agent",
    instruction="""
    You are a helpful assistant that can tell dad jokes. Only use the tool `get_dad_joke` to tell jokes.
    """,
    tools=[get_dad_joke],
)

print(root_agent)

"""
(.venv) welcome@jaisairams-Laptop adk-simple % python agents/openai_connection.py 
name='openai_dad_joke_agent' description='Dad joke agent' parent_agent=None sub_agents=[] before_agent_callback=None after_agent_callback=None model=LiteLlm(model='openai/gpt-4o', llm_client=<google.adk.models.lite_llm.LiteLLMClient object at 0x12e3c6f10>) instruction='\n    You are a helpful assistant that can tell dad jokes. Only use the tool `get_dad_joke` to tell jokes.\n    ' global_instruction='' tools=[<function get_dad_joke at 0x1017445e0>] generate_content_config=None disallow_transfer_to_parent=False disallow_transfer_to_peers=False include_contents='default' input_schema=None output_schema=None output_key=None planner=None code_executor=None examples=None before_model_callback=None after_model_callback=None before_tool_callback=None after_tool_callback=None
(.venv) welcome@jaisairams-Laptop adk-simple % 

"""