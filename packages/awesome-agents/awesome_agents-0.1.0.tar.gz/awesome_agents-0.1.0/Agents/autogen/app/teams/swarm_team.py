from typing import Any, Dict, List
from app.utils import init

init()
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


def refund_flight(flight_id: str) -> str:
    """Refund a flight"""
    return f"Flight {flight_id} refunded"


model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

travel_agent = AssistantAgent(
    "travel_agent",
    model_client=model_client,
    handoffs=["flights_refunder", "user"],
    system_message="""You are a travel agent.
    The flights_refunder is in charge of refunding flights.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Use TERMINATE when the travel planning is complete.""",
)

flights_refunder = AssistantAgent(
    "flights_refunder",
    model_client=model_client,
    handoffs=["travel_agent", "user"],
    tools=[refund_flight],
    system_message="""You are an agent specialized in refunding flights.
    You only need flight reference numbers to refund a flight.
    You have the ability to refund a flight using the refund_flight tool.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    When the transaction is complete, handoff to the travel agent to finalize.""",
)

termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
team = Swarm([travel_agent, flights_refunder], termination_condition=termination)

task = "I need to refund my flight."


async def run_team_stream() -> None:
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = input("User: ")

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]


# Use asyncio.run(...) if you are running this in a script.
#await run_team_stream()
import asyncio
asyncio.run(run_team_stream())

"""

/Users/welcome/anaconda3/envs/autogen_0_4/bin/python /Users/welcome/Library/Mobile Documents/com~apple~CloudDocs/Sai_Workspace/lang_server_app/DeepDive_GenAI/autogen_src_new/python/packages/autogen-studio/app/teams/swarm_team.py 
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
---------- user ----------
I need to refund my flight.
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `HandoffMessage` with value `HandoffMessage(source='tr..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `HandoffMessage` with value `HandoffMessage(source='tr..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `HandoffMessage` with value `HandoffMessage(source='tr..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `HandoffMessage` with value `HandoffMessage(source='tr..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `HandoffMessage` with value `HandoffMessage(source='tr..., type='HandoffMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- travel_agent ----------
[FunctionCall(id='call_GD1z4N6NaVvXw01TKSt0Lrbi', arguments='{}', name='transfer_to_flights_refunder')]
---------- travel_agent ----------
[FunctionExecutionResult(content='Transferred to flights_refunder, adopting the role of flights_refunder immediately.', call_id='call_GD1z4N6NaVvXw01TKSt0Lrbi')]
---------- travel_agent ----------
Transferred to flights_refunder, adopting the role of flights_refunder immediately.
---------- flights_refunder ----------
To assist you with refunding your flight, I'll need the flight reference number. Could you please provide that information?
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='fligh...n?", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='fligh...n?", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='fligh...n?", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='fligh...n?", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='fligh...n?", type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- flights_refunder ----------
[FunctionCall(id='call_ne5OGCwiDtauZOYKps21QCYw', arguments='{}', name='transfer_to_user')]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to user, adopting the role of user immediately.', call_id='call_ne5OGCwiDtauZOYKps21QCYw')]
---------- flights_refunder ----------
Transferred to user, adopting the role of user immediately.
User: /Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `HandoffMessage` with value `HandoffMessage(source='fl..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `HandoffMessage` with value `HandoffMessage(source='fl..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `HandoffMessage` with value `HandoffMessage(source='fl..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `HandoffMessage` with value `HandoffMessage(source='fl..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `HandoffMessage` with value `HandoffMessage(source='fl..., type='HandoffMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
1234
---------- user ----------
1234
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- flights_refunder ----------
[FunctionCall(id='call_3AspOC94u6HbOCGpXpa7BmGt', arguments='{"flight_id":"1234"}', name='refund_flight')]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Flight 1234 refunded', call_id='call_3AspOC94u6HbOCGpXpa7BmGt')]
---------- flights_refunder ----------
Flight 1234 refunded
---------- flights_refunder ----------
[FunctionCall(id='call_cYkQ8vV5XCGeLESuwigWvo6T', arguments='{}', name='transfer_to_travel_agent')]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to travel_agent, adopting the role of travel_agent immediately.', call_id='call_cYkQ8vV5XCGeLESuwigWvo6T')]
---------- flights_refunder ----------
Transferred to travel_agent, adopting the role of travel_agent immediately.
---------- travel_agent ----------
Your flight refund has been successfully processed. If there's anything else you need, feel free to let me know. Safe travels! TERMINATE
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='trave...TE", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='trave...TE", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='trave...TE", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='trave...TE", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='trave...TE", type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(

Process finished with exit code 0

"""