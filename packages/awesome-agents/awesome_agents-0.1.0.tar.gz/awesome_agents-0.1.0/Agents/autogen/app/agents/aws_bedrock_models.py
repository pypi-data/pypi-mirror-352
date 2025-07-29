import boto3
import asyncio
from botocore.config import Config

from autogen_core.models import ModelInfo, ModelFamily
from autogen_ext.models.semantic_kernel import SKChatCompletionAdapter

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.bedrock import BedrockChatCompletion, BedrockChatPromptExecutionSettings
from semantic_kernel.memory.null_memory import NullMemory

my_config = Config(
    region_name = 'us-east-1',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    },
)

# Create the custom boto3 client
#bedrock_runtime_client = boto3.client(service_name='bedrock-runtime', config=my_config)
#bedrock_client = boto3.client("bedrock", config=my_config)
bedrock_runtime_client = boto3.client(service_name='bedrock-runtime')
bedrock_client = boto3.client("bedrock")

sk_client = BedrockChatCompletion(
    model_id='anthropic.claude-3-5-sonnet-20240620-v1:0',
    runtime_client=bedrock_runtime_client,
    client=bedrock_client,
)

# Configure execution settings
settings = BedrockChatPromptExecutionSettings(
    temperature=0.7,
    max_tokens=1000,
)

model_info = ModelInfo(vision=False, function_calling=True, json_output=True, family=ModelFamily.UNKNOWN)
model_client = SKChatCompletionAdapter(
    sk_client,
    kernel=Kernel(memory=NullMemory()),
    prompt_settings=settings,
    model_info=model_info,
)

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

async def get_weather(city: str) -> str:
    """Get the current weather for a given city"""
    return f"The weather in {city} is 73 degrees and Sunny."

async def main() -> None:
    weather_agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
       tools=[get_weather],
        system_message="You are a helpful AI assistant that can provide weather information.",
        model_client_stream=True,
    )
    print("Registered tools:", [tool.name for tool in weather_agent._tools])

    stream = weather_agent.on_messages_stream(
        [TextMessage(content="Weather in Shanghai", source="user")], CancellationToken()
    )
    #stream=weather_agent.run_stream(task="What is best places in Media PA ,USA")
    async for response in stream:
        print(response)

asyncio.run(main())