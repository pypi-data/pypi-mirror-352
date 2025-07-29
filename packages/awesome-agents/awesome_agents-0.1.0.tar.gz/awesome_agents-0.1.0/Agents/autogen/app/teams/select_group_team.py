from autogen_ext.models.openai import OpenAIChatCompletionClient

from app.utils import init

init()
# Note: This example uses mock tools instead of real APIs for demonstration purposes
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console


def search_web_tool(query: str) -> str:
    if "2006-2007" in query:
        return """Here are the total points scored by Miami Heat players in the 2006-2007 season:
        Udonis Haslem: 844 points
        Dwayne Wade: 1397 points
        James Posey: 550 points
        ...
        """
    elif "2007-2008" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214."
    elif "2008-2009" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398."
    return "No data found."


def percentage_change_tool(start: float, end: float) -> float:
    return ((end - start) / start) * 100


model_client = OpenAIChatCompletionClient(model="gpt-4o")

planning_agent = AssistantAgent(
    "PlanningAgent",
    description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
    model_client=model_client,
    system_message="""
    You are a planning agent.
    Your job is to break down complex tasks into smaller, manageable subtasks.
    Your team members are:
        WebSearchAgent: Searches for information
        DataAnalystAgent: Performs calculations

    You only plan and delegate tasks - you do not execute them yourself.

    When assigning tasks, use this format:
    1. <agent> : <task>

    After all tasks are complete, summarize the findings and end with "TERMINATE".
    """,
)

web_search_agent = AssistantAgent(
    "WebSearchAgent",
    description="An agent for searching information on the web.",
    tools=[search_web_tool],
    model_client=model_client,
    system_message="""
    You are a web search agent.
    Your only tool is search_tool - use it to find information.
    You make only one search call at a time.
    Once you have the results, you never do calculations based on them.
    """,
)

data_analyst_agent = AssistantAgent(
    "DataAnalystAgent",
    description="An agent for performing calculations.",
    model_client=model_client,
    tools=[percentage_change_tool],
    system_message="""
    You are a data analyst.
    Given the tasks you have been assigned, you should analyze the data and provide results using the tools provided.
    If you have not seen the data, ask for it.
    """,
)

text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination

selector_prompt = """Select an agent to perform task.

{roles}

Current conversation context:
{history}

Read the above conversation, then select an agent from {participants} to perform the next task.
Make sure the planner agent has assigned tasks before other agents start working.
Only select one agent.
"""

team = SelectorGroupChat(
    [planning_agent, web_search_agent, data_analyst_agent],
    model_client=model_client,
    termination_condition=termination,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=True,  # Allow an agent to speak multiple turns in a row.
)

task = "Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?"


async def main():
    # Use asyncio.run(...) if you are running this in a script.
    await Console(team.run_stream(task=task))

import asyncio
asyncio.run(main())

"""

/Users/welcome/anaconda3/envs/autogen_0_4/bin/python /Users/welcome/Library/Mobile Documents/com~apple~CloudDocs/Sai_Workspace/lang_server_app/DeepDive_GenAI/autogen_src_new/python/packages/autogen-studio/app/teams/select_group_team.py 
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
---------- user ----------
Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
---------- PlanningAgent ----------
To break this down, we need two main pieces of information:

1. Identify the Miami Heat player with the highest points in the 2006-2007 NBA season.
2. Calculate the percentage change in total rebounds for that player between the 2007-2008 and 2008-2009 seasons.

Here are the tasks to gather and analyze the needed information:

1. WebSearchAgent: Find the Miami Heat player with the highest points in the 2006-2007 NBA season.
2. WebSearchAgent: Retrieve the total rebounds for this player in the 2007-2008 season.
3. WebSearchAgent: Retrieve the total rebounds for this player in the 2008-2009 season.
4. DataAnalystAgent: Calculate the percentage change in total rebounds between the 2007-2008 and 2008-2009 seasons.

Upon completion of these tasks, we will have the complete answer.
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='Plann...r.', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='Plann...r.', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='Plann...r.', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='Plann...r.', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='Plann...r.', type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- WebSearchAgent ----------
[FunctionCall(id='call_fs7yqlCWIUYFkFqiPobRkfiF', arguments='{"query":"Miami Heat highest scoring player 2006-2007 season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', call_id='call_fs7yqlCWIUYFkFqiPobRkfiF')]
---------- WebSearchAgent ----------
Here are the total points scored by Miami Heat players in the 2006-2007 season:
        Udonis Haslem: 844 points
        Dwayne Wade: 1397 points
        James Posey: 550 points
        ...
        
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- WebSearchAgent ----------
[FunctionCall(id='call_j6ep73CBxr6OFDUU8WFd2XWS', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool'), FunctionCall(id='call_jbp12nJF0NdT8jmuevMM15D4', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_j6ep73CBxr6OFDUU8WFd2XWS'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_jbp12nJF0NdT8jmuevMM15D4')]
---------- WebSearchAgent ----------
The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.
The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
---------- DataAnalystAgent ----------
[FunctionCall(id='call_ue2CW2qKrkT53xe1lt3UYdCp', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
---------- DataAnalystAgent ----------
[FunctionExecutionResult(content='85.98130841121495', call_id='call_ue2CW2qKrkT53xe1lt3UYdCp')]
---------- DataAnalystAgent ----------
85.98130841121495
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='Plann...TE", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='Plann...TE", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='Plann...TE", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='Plann...TE", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='Plann...TE", type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- PlanningAgent ----------
Here's the summarized information:

1. The Miami Heat player with the highest points in the 2006-2007 season was Dwyane Wade, with 1,397 points.
2. For Dwyane Wade, the total rebounds in the 2007-2008 season were 214, and in the 2008-2009 season, they were 398, representing a percentage increase of approximately 85.98%.

TERMINATE

Process finished with exit code 0

"""