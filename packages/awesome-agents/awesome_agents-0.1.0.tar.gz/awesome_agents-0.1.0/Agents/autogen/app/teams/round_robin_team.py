import asyncio

from app.utils import init

init()
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Create an OpenAI model client.
model_client = OpenAIChatCompletionClient(
    model="gpt-4o-2024-08-06",
    # api_key="sk-...", # Optional if you have an OPENAI_API_KEY env variable set.
)

# Create the primary agent.
primary_agent = AssistantAgent(
    "primary",
    model_client=model_client,
    system_message="You are a helpful AI assistant.",
)

# Create the critic agent.
critic_agent = AssistantAgent(
    "critic",
    model_client=model_client,
    system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
)

# Define a termination condition that stops the task if the critic approves.
text_termination = TextMentionTermination("APPROVE")

# Create a team with the primary and critic agents.
team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)


async def main():
    # Use `asyncio.run(...)` when running in a script.
    #result = await team.run(task="Write a short poem about the fall season.")
    #print(result)
    #await team.reset()  # Reset the team for a new task.
    async for message in team.run_stream(task="Write a short poem about the fall season."):  # type: ignore
        if isinstance(message, TaskResult):
            print("Stop Reason:", message.stop_reason)
        else:
            print(message)


import asyncio

asyncio.run(main())

"""
/Users/welcome/anaconda3/envs/autogen_0_4/bin/python /Users/welcome/Library/Mobile Documents/com~apple~CloudDocs/Sai_Workspace/lang_server_app/DeepDive_GenAI/autogen_src_new/python/packages/autogen-studio/app/teams/round_robin_team.py 
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client" in AssistantAgentConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_context" in AssistantAgentConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client_stream" in AssistantAgentConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client" in SocietyOfMindAgentConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client" in MagenticOneGroupChatConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client" in SelectorGroupChatConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_capabilities" in BaseOpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_info" in BaseOpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_capabilities" in OpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_info" in OpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_capabilities" in AzureOpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_info" in AzureOpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='prima...  ", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='prima...  ", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='prima...  ", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='prima...  ", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='prima...  ", type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='criti...l!', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='criti...l!', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='criti...l!', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='criti...l!', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='criti...l!', type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='prima...r!", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='prima...r!", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='prima...r!", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='prima...r!", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='prima...r!", type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='criti...VE', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='criti...VE', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='criti...VE', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='criti...VE', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='criti...VE', type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Write a short poem about the fall season.', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=109), content="Leaves of amber, gold, and rust,  \nDance gently down in autumn's gust.  \nCrisp air whispers through the trees,  \nAs branches sway with graceful ease.  \n\nPumpkin patches, harvest moon,  \nBonfires crackle, night's cocoon.  \nSweaters cozy, cider warm,  \nNature dons its vibrant charm.  \n\nBeneath this painted, tranquil sky,  \nA time to bid the summer goodbye.  \nIn every breeze, a soft embrace,  \nFall wraps the world in its gentle grace.  ", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=154, completion_tokens=147), content='Your poem beautifully captures the essence of the fall season with vivid imagery and a soothing rhythm. The imagery of "Leaves of amber, gold, and rust" and "Pumpkin patches, harvest moon" effectively paints a picture of the season\'s colors and activities.\n\nTo enhance the poem further, consider incorporating more sensory details to engage the reader\'s other senses fully. For example, you might describe the sound of leaves crunching underfoot or the smell of spiced cider wafting through the air. Additionally, experimenting with a unique metaphor or simile could add an extra layer of depth to your descriptions. \n\nOverall, your poem resonates with warmth and nostalgia, making it an enjoyable read. Great job capturing the essence of fall!', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=294, completion_tokens=189), content="Thank you for your thoughtful feedback! I'm glad you enjoyed the poem. Here's a revised version with more sensory details and a touch of metaphor:\n\nLeaves of amber, gold, and rust,  \nDance gently down in autumn's gust.  \nCrisp air whispers through the trees,  \nAs branches sway with graceful ease.  \n\nPumpkin patches, harvest moon,  \nBonfires crackle, night's cocoon.  \nUnderfoot, the leaves do crunch,  \nSpiced cider drifts, a fragrant punch.  \n\nSweaters cozy, warmth enshrined,  \nFall paints the world with colors kind.  \nNature's quilt, a woven sphere,  \nWraps the earth in autumn's cheer.  \n\nIn this embrace, both soft and grand,  \nSummer bows to autumn's hand.  \nThe world, a canvas brightly drawn,  \nIn hues of dusk and early dawn.  \n\nI hope this version captures the essence you're looking for!", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=500, completion_tokens=181), content='Your revised poem enriches the sensory experience and beautifully incorporates metaphor to elevate its imagery. The addition of "Underfoot, the leaves do crunch" and "Spiced cider drifts, a fragrant punch" successfully engages the senses of sound and smell, enhancing the reader\'s immersion in the scene.\n\nThe metaphor of "Nature\'s quilt, a woven sphere" wraps the reader in a cozy, vivid image, effectively conveying the warmth and comfort of the fall season. The closing lines, "In this embrace, both soft and grand, / Summer bows to autumn\'s hand," provide a lovely transition between seasons, and the final imagery of "The world, a canvas brightly drawn, / In hues of dusk and early dawn" leaves a lasting impression.\n\nOverall, this version of the poem beautifully captures the essence of fall with its enriched imagery, sensory details, and metaphorical language. Well done! APPROVE', type='TextMessage')], stop_reason="Text 'APPROVE' mentioned")

Process finished with exit code 0


"""