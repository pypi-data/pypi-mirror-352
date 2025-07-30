# Trento Agent SDK

The Trento Agent SDK is a comprehensive toolkit for building AI agents that can communicate with each other, use tools, and maintain memory of past interactions.

## Installation

```bash
pip install -r requirements.txt
```

## Key Features

- **Agent-to-Agent Communication**: Enables agents to communicate with each other using the A2A protocol
- **Tool Management**: Register, manage, and execute tools that agents can use
- **Memory Management**: Short-term and long-term memory for agents to remember past interactions
- **Performance Optimizations**: Parallel tool execution, connection pooling, and caching

## Quick Start

### Running the Summarization Agent

```bash
streamlit run summarizerAgent.py
```

### Creating an Agent Server

```python
from trento_agent_sdk import Agent, ToolManager, A2AServer, AgentCard, TaskManager

# Create a tool manager
tool_manager = ToolManager()

# Register tools
tool_manager.add_tool(
    fn=my_tool_function,
    name="my_tool"
)

# Create an agent
agent = Agent(
    name="My Agent",
    model="gemini-2.0-flash",
    tool_manager=tool_manager
)

# Define the agent's capabilities
agent_card = AgentCard(
    name="My Agent",
    description="An agent that can perform tasks",
    skills=[
        {"name": "my_skill", "description": "A description of what this agent can do"}
    ]
)

# Create a task manager
task_manager = TaskManager()

# Create and run the server
server = A2AServer(
    agent=agent,
    agent_card=agent_card,
    task_manager=task_manager,
    port=8000
)

server.run()
```

See the [improved documentation](IMPROVEMENTS.md) for information about the recent performance and reliability enhancements.