# What is Agent 
```
An agent is an AI model configured with instructions, tools, guardrails, handoffs and more.

We strongly recommend passing `instructions`, which is the "system prompt" for the agent. In
addition, you can pass `handoff_description`, which is a human-readable description of the
agent, used when the agent is used inside tools/handoffs.

Agents are generic on the context type. The context is a (mutable) object you create. It is
passed to tool functions, handoffs, guardrails, etc.


Understanding the Agent Loop
When you call Runner.run(), the SDK initiates what's called the "agent loop":

The agent receives the input
The LLM processes the input based on the agent’s instructions
If the LLM produces a final output (text without tool calls), the loop ends
If the LLM calls a tool or requests a handoff, those are processed, and the loop continues
This repeats until a final output is produced or the maximum number of turns is reached

Run a workflow starting at the given agent. The agent will run in a loop until a final
        output is generated. The loop runs like so:
1. The agent is invoked with the given input.
2. If there is a final output (i.e. the agent produces something of type
    `agent.output_type`, the loop terminates.
3. If there's a handoff, we run the loop again, with the new agent.
4. Else, we run tool calls (if any), and re-run the loop.

In two cases, the agent may raise an exception:
1. If the max_turns is exceeded, a MaxTurnsExceeded exception is raised.
2. If a guardrail tripwire is triggered, a GuardrailTripwireTriggered exception is raised.

Note that only the first agent's input guardrails are run.



```


# Deep Dive about OpenAI Agents SDK
```angular2html


OpenAI Agents SDK: A Comprehensive Guide to Building Agentic AI Applications from AgentOps and Agency AI
OpenAI has recently released the Agents SDK, a powerful yet lightweight framework designed to help developers build agentic AI applications with minimal abstractions. This production-ready toolkit represents an evolution from OpenAI’s previous experimental work on agents known as Swarm. The Agents SDK provides a streamlined approach to creating AI systems that can reason, plan, and take actions to accomplish complex tasks.

In this comprehensive guide, we’ll explore the core concepts, features, and use cases of the Agents SDK, examining how it enables developers to create sophisticated AI applications without a steep learning curve. Note that if your intention is to build an enterprise-grade agent, we recommend installing AgentOps before your first run so you can track everything your agent is doing both in testing and production. Tracing and Observability from AgentOps enables every use track every LLM call, tool being used, API call, and everything your agent does. AgentOps is totally LLM provider agnostic.

If your team needs help building agents end-to-end, Agency AI is the worlds leading agent consulting firm having built agents for everyone from Series B startups to Fortune 500 companies.

Core Concepts of the Agents SDK
The Agents SDK is built around a small set of powerful primitives that, when combined with Python, allow developers to express complex relationships between tools and agents:

Agents

At the heart of the SDK are Agents, which are essentially LLMs (Large Language Models) equipped with instructions and tools. An agent represents an AI model configured with specific capabilities, knowledge, and behaviors. Each agent has a name, instructions (which serve as its “system prompt”), and can be equipped with various tools, guardrails, and handoff capabilities.

Agents can be specialized for particular tasks, such as customer support, code generation, or data analysis. The instructions provided to an agent define its behavior, knowledge boundaries, and how it should respond to different inputs.

Handoffs

Handoffs allow agents to delegate tasks to other agents for specific purposes. This powerful feature enables the creation of modular, specialized agents that excel at particular tasks. For example, a triage agent might receive a user query and then hand off to a specialized agent based on the nature of the request.

Handoffs are represented as tools to the LLM, making them a natural part of the agent’s decision-making process. When a handoff occurs, the new agent takes over the conversation, seeing the entire previous conversation history (unless modified by input filters).

Guardrails

Guardrails enable inputs to agents to be validated, providing a way to ensure that agents operate within defined boundaries. They run in parallel to your agents, allowing for checks and validations of user input or agent output.

There are two types of guardrails:

Input guardrails: Run on the initial user input
Output guardrails: Run on the final agent output
Guardrails can include “tripwires” that, when triggered, immediately halt the agent’s execution and raise an exception, allowing developers to handle problematic inputs or outputs appropriately.

Tracing

AgentOps.ai is the leader in agent tracing and observability and integrates directly into the SDK. The SDK includes built-in tracing capabilities that let developers visualize and debug their agentic flows. Tracing records all events that occur during an agent run, including LLM generations, tool calls, handoffs, guardrails, and even custom events.

This feature is invaluable for debugging, visualization, and monitoring workflows during both development and production. Traces consist of spans that represent operations with start and end times, providing a detailed view of what happened during an agent’s execution.

Key Features of the Agents SDK
Agent Loop
The SDK includes a built-in agent loop that handles calling tools, sending results to the LLM, and looping until the LLM is done. This loop manages the entire process of agent execution, from initial input to final output.

When you call Runner.run(), the SDK runs a loop until a final output is generated:

The agent is invoked with the given input
If there is a final output, the loop terminates
If there’s a handoff, the loop runs again with the new agent
Otherwise, tool calls are processed, and the loop runs again
This automated loop simplifies the development process, handling the complex orchestration of agent actions behind the scenes.

Python-First Approach
The SDK is designed to be Python-first, allowing developers to use built-in language features to orchestrate and chain agents, rather than needing to learn new abstractions. This approach makes the SDK accessible to developers already familiar with Python, reducing the learning curve.

Function Tools
The SDK makes it easy to turn any Python function into a tool, with automatic schema generation and Pydantic-powered validation. This allows agents to interact with external systems, databases, APIs, or perform computations through simple function calls.

Advanced Features and Patterns
Dynamic Instructions
While most agents have static instructions defined at creation time, the SDK also supports dynamic instructions via a function. This function receives the agent and context and must return the prompt, allowing for context-dependent agent behavior.

Lifecycle Events (Hooks)
Developers can hook into the agent lifecycle with the hooks property, allowing them to observe and respond to various events during an agent’s execution. This is useful for logging, monitoring, or pre-fetching data when certain events occur.

Final Output Handling
There are two ways to get a final output from an agent:

If an output_type is set on the agent, the LLM is given a special tool called final_output. When it uses this tool, the output becomes the final output.
If no output_type is specified, the final output is assumed to be a string. As soon as the LLM produces a message without any tool calls, that becomes the final output.
Streaming
The SDK supports streaming, allowing developers to receive events as they are generated by the LLM. This is particularly useful for creating responsive user interfaces that display AI responses as they are being generated.

Run Configuration

The run_config parameter allows developers to configure global settings for an agent run, including model settings, handoff input filters, tracing options, and more. This provides flexibility in how agents are executed and monitored.

Common Agent Patterns
The Agents SDK enables several powerful patterns for building complex AI applications:

Deterministic Flows
A common tactic is to break down a task into a series of smaller steps, each performed by an agent. The output of one agent becomes the input to the next, creating a deterministic workflow. For example, a story generation task might be broken down into generating an outline, writing the story, and creating an ending.

Handoffs and Routing
Specialized sub-agents can handle specific tasks, with handoffs used to route tasks to the right agent. For instance, a frontline agent might receive a request and then hand off to a specialized agent based on the language or content of the request.

Agents as Tools
Instead of using handoffs where a new agent “takes over,” agents can also be used as tools. In this pattern, the tool agent runs independently and returns a result to the original agent, enabling parallel processing of multiple tasks.

LLM-as-a-Judge
LLMs can improve the quality of their output when given feedback. A common pattern is to generate a response using one model and then use a second model to provide feedback. This feedback can then be used to improve the response, creating an iterative improvement cycle.

Parallelization
Running multiple agents in parallel can improve latency when steps don’t depend on each other or enable strategies like generating multiple responses and selecting the best one.

Use Cases for the Agents SDK
The Agents SDK is versatile and can be applied to a wide range of use cases:

Customer Support

Agents can be designed to handle customer inquiries, with specialized agents for different types of requests (billing, technical support, refunds, etc.). Guardrails ensure that sensitive information is handled appropriately, and tracing helps monitor and improve the customer experience.

Content Generation

Agents can generate various types of content, from blog posts to marketing copy, with specialized agents handling different aspects of the content creation process. The LLM-as-a-judge pattern can be used to evaluate and improve the quality of generated content.

Code Generation and Analysis

Specialized agents can generate code, analyze existing code, or help with debugging, with handoffs to more specialized agents for specific programming languages or frameworks.

Research and Data Analysis

Agents can assist with research tasks, analyzing data, and generating insights, with specialized agents for different types of analysis or data sources.

Tracing and Debugging
Tracing and Observability from AgentOps enables every use track every LLM call, tool being used, API call, and everything your agent does. AgentOps is totally LLM provider agnostic.

The tracing capabilities of the Agents SDK are particularly powerful for debugging and monitoring agent behavior:

Traces and Spans
Traces represent a single end-to-end operation of a workflow, composed of spans. They include properties like workflow name, trace ID, and session ID.

Spans represent operations with start and end times, containing information about the operation, such as agent actions, LLM generations, tool calls, etc.

Default Tracing
By default, the SDK traces the entire agent run, including agent operations, LLM generations, function tool calls, guardrails, and handoffs. This comprehensive tracing provides a detailed view of what happened during an agent’s execution.

Higher-Level Traces
Developers can create higher-level traces that span multiple agent runs, allowing for a more holistic view of complex workflows. This is useful for understanding how different agents interact over time.

Sensitive Data Handling
The SDK provides options for handling potentially sensitive data in traces, allowing developers to exclude sensitive information from traces while still maintaining the overall structure of the trace.

Guardrails
Guardrails provide a powerful mechanism for ensuring that agents operate within defined boundaries:

Input Guardrails
Input guardrails run on the initial user input, checking for issues like off-topic requests, malicious content, or requests that the agent is not designed to handle. If an input guardrail’s tripwire is triggered, the agent execution is immediately halted.

Output Guardrails
Output guardrails run on the final agent output, ensuring that the agent’s response meets certain criteria before being returned to the user. This can include checks for accuracy, appropriateness, or compliance with specific guidelines.

Tripwires
Tripwires provide a mechanism for immediately halting agent execution when certain conditions are met. This is particularly useful for quickly rejecting invalid inputs or preventing inappropriate outputs.

Conclusion
The OpenAI Agents SDK represents a significant step forward in making agentic AI applications more accessible to developers. With its lightweight, Python-first approach and powerful primitives, the SDK enables the creation of sophisticated AI systems without a steep learning curve.

By providing built-in support for agents, handoffs, guardrails, and tracing, the SDK addresses many of the common challenges in building agentic AI applications. The various patterns and use cases demonstrate the versatility of the SDK, making it suitable for a wide range of applications.

Whether you’re building a customer support system, a content generation platform, or a code analysis tool, the Agents SDK provides the building blocks you need to create powerful, flexible, and reliable AI applications. With its focus on simplicity, flexibility, and robustness, the SDK is poised to become an essential tool for developers working with agentic AI.

If your team needs help building with the Agents SDK, reach out to Agency AI, the worlds best AI agent consulting firm.


```