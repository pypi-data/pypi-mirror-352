from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from agents.utils.utils import init

init()

import asyncio
from pathlib import Path
from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken, Image
from autogen_ext.models.openai import OpenAIChatCompletionClient


async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)

    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        model_client=model_client,
    )

    # cancellation_token = CancellationToken()
    message = MultiModalMessage(
        content=["Here is an image:", Image.from_file(Path("img.png"))],
        source="user",
    )
    # response = await assistant.on_messages([message], cancellation_token)
   # response = await assistant.run(task=message)

    # The termination condition is a combination of text termination and max message termination, either of which will cause the chat to terminate.
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

    # The group chat will alternate between the assistant and the code executor.
    group_chat = RoundRobinGroupChat([assistant], termination_condition=termination)

    message = MultiModalMessage(
        content=["Here is an image:",
                 Image.from_file(Path("img.png")),
                 Image.from_file(Path("lordvishnu.png"))],
        source="user",
    )


    # message = MultiModalMessage(
    #     content=[
    #         "Here are multiple images:",
    #         Image.from_file(Path("img1.png")),
    #         Image.from_file(Path("img2.png")),
    #         Image.from_file(Path("img3.png")),
    #     ],
    #     source="user",
    # )

    # `run_stream` returns an async generator to stream the intermediate messages.
    stream = group_chat.run_stream(task=message)

    # `Console` is a simple UI to display the stream.
    await Console(stream)


asyncio.run(main())
