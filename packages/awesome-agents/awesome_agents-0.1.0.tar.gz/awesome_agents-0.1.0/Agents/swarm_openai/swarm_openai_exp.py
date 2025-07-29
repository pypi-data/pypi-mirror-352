from swarm import Agent
from agents.utils.utils import init

init()


# creating handoffs functions
def handoff_to_weather_agent():
    """Transfer to the weather agent for weather queries."""
    print("Handing off to Weather Agent")
    return weather_agent


def handoff_to_math_agent():
    """Transfer to the math agent for mathematical queries."""
    print("Handing off to Math Agent")
    return math_agent


# Initialize the agents with specific roles
math_agent = Agent(
    name="Math Agent",
    instructions="You handle only mathematical queries.",
    functions=[handoff_to_weather_agent]
)

weather_agent = Agent(
    name="Weather Agent",
    instructions="You handle only weather-related queries.",
    functions=[handoff_to_math_agent]
)

print(weather_agent)
