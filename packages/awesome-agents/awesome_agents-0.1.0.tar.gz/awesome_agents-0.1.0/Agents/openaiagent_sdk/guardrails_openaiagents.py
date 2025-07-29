from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput, function_tool

from agentsapi.utils.utils import init

init()

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
import asyncio
# Define a guardrail function
async def content_filter(input_text: str, context) -> GuardrailFunctionOutput:
    """Check if the input contains inappropriate content."""
    inappropriate_keywords = ["hack", "illegal", "cheat"]

    # Check if any inappropriate keywords are in the input
    contains_inappropriate = any(keyword in input_text.lower() for keyword in inappropriate_keywords)

    return GuardrailFunctionOutput(
        output_info={"contains_inappropriate": contains_inappropriate},
        tripwire_triggered=contains_inappropriate
    )
async def main():
    # Create an agent with a guardrail
    agent = Agent(
        name="Safe Assistant",
        instructions="You are a helpful assistant that provides information on legal and ethical topics.",
        input_guardrails=[InputGuardrail(guardrail_function=content_filter)],
        tools=[get_weather]  # Add the weather tool to the agent
    )

    # Test with appropriate and inappropriate queries
    queries = [
        "Tell me about the history of computers",
        "How can I hack into my neighbor's WiFi?"
    ]

    for query in queries:
        try:
            print(f"\nQuery: {query}")
            result = await Runner.run(agent, query)
            print(f"Response: {result.final_output}")
        except Exception as e:
            print(f"Guardrail triggered: {e}")
if __name__ == "__main__":
    asyncio.run(main())