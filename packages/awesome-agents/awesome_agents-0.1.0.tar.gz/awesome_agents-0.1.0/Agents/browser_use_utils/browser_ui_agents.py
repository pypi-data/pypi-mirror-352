from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio

from agentsapi.utils.utils import init

init()


async def main():
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    await agent.run()


asyncio.run(main())
