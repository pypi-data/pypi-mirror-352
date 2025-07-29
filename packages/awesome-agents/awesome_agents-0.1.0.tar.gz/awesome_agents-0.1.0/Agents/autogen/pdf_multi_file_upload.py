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
import fitz  # PyMuPDF for PDF processing


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_images_from_pdf(pdf_path: Path) -> list[Image]:
    """Extract images from a PDF file."""
    images = []
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc):
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                image = Image.from_bytes(image_data)
                images.append(image)
    return images


async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)

    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        model_client=model_client,
    )

    # Path to the PDF file
    pdf_path = Path("agents.pdf")

    # Extract text and images from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    #pdf_images = extract_images_from_pdf(pdf_path)

    # # Create a MultiModalMessage with the extracted content
    # message = MultiModalMessage(
    #     content=["Here is the content from the PDF:", pdf_text, *pdf_images],
    #     source="user",
    # )
    # Create a MultiModalMessage with the extracted content
    message = MultiModalMessage(
        content=["Here is the content from the PDF:", pdf_text],
        source="user",
    )

    # Send the message to the assistant
    response = await assistant.run(task=message)

    # Termination condition
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

    # Group chat setup
    group_chat = RoundRobinGroupChat([assistant], termination_condition=termination)

    # Stream the response
    stream = group_chat.run_stream(task=message)

    # Display the stream in the console
    await Console(stream)


asyncio.run(main())