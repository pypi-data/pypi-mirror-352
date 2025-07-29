from agents import Agent, Runner, function_tool
import asyncio

from agentsapi.utils.utils import init

init()

# Define a tool as a Python function
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In a real application, this would call a weather API
    weather_data = {
        "New York": "72°F, Sunny",
        "London": "65°F, Cloudy",
        "Tokyo": "80°F, Clear",
        "Paris": "70°F, Partly Cloudy"
    }
    return weather_data.get(city, f"Weather data not available for {city}")


async def main():
    # Create an agent with the weather tool
    agent = Agent(
        name="Weather Assistant",
        instructions="You are a helpful assistant that provides weather information when asked.",
        tools=[get_weather]  # Add the tool to the agent
    )

    # Run the agent with a user query
    result = await Runner.run(agent, "What's the weather like in Tokyo?")

    # Print the final output
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
