``
Magentic-One
Magentic-One is a generalist multi-agent system for solving open-ended web and file-based tasks across a variety of domains. It represents a significant step forward for multi-agent systems, achieving competitive performance on a number of agentic benchmarks (see the technical report for full details).

When originally released in November 2024 Magentic-One was implemented directly on the autogen-core library. We have now ported Magentic-One to use autogen-agentchat, providing a more modular and easier to use interface.

To this end, the Magentic-One orchestrator MagenticOneGroupChat is now simply an AgentChat team, supporting all standard AgentChat agents and features. Likewise, Magentic-One’s MultimodalWebSurfer, FileSurfer, and MagenticOneCoderAgent agents are now broadly available as AgentChat agents, to be used in any AgentChat workflows.

Lastly, there is a helper class, MagenticOne, which bundles all of this together as it was in the paper with minimal configuration.

Find additional information about Magentic-one in our blog post and technical report.

``