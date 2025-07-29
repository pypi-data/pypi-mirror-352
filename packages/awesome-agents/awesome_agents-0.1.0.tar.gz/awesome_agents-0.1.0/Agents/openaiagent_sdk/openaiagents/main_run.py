import os
from dotenv import load_dotenv
import agentops

from Agents.openaiagent_sdk.openaiagents.main_agent import health_coach
from agentsapi.utils.utils import init

init()
# Load environment variables from .env file
# Get API key from environment variables
AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
print(f"Using AgentOps API Key: {AGENTOPS_API_KEY}")
# Initialize AgentOps - this is all you need for automatic instrumentation
agentops.init(api_key=AGENTOPS_API_KEY, default_tags=["wellness_coach"])

import asyncio
from agents import Runner


async def main():
    print("Welcome to the Health and Wellness Coach!")
    print("I can help you with workouts, nutrition, sleep, and general wellness advice.")
    print("Type 'exit' at any time to end the conversation.\n")

    query = input("How can I help with your health and wellness goals today? ")

    while query.lower() != 'exit':
        try:
            # Run the agent - AgentOps will automatically track this
            result = await Runner.run(health_coach, query)

            # Print the response to the user
            print(f"\nHealth Coach: {result.final_output}\n")

        except Exception as e:
            print(f"\nAn error occurred: {str(e)}\n")

        # Get the next query
        query = input("You: ")


if __name__ == "__main__":
    asyncio.run(main())
