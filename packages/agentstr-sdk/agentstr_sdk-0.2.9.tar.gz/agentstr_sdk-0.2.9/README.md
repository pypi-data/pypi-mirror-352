# Agentstr SDK

[![Documentation](https://img.shields.io/badge/docs-online-blue.svg)](https://agentstr.com/docs)
[![PyPI](https://img.shields.io/pypi/v/agentstr-sdk)](https://pypi.org/project/agentstr-sdk/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Overview

Agentstr SDK is a powerful toolkit for building decentralized agentic applications on the Nostr protocol. It provides seamless integration with [MCP (Model Context Protocol)](https://modelcontextprotocol.io/introduction), [A2A (Agent-to-Agent)](https://google-a2a.github.io/A2A/), and multiple popular agentic frameworks like [Agno](https://docs.agno.com/introduction), [DSPy](https://dspy.ai/), and [LangGraph](https://www.langchain.com/langgraph).

To ensure full stack decentralization, we recommend using [Routstr](https://routstr.com) as your LLM provider.

## Features

### Core Components
- **Nostr Integration**: Full support for Nostr protocol operations
  - Event publishing and subscription
  - Direct messaging
  - Metadata handling
- **Lightning Integration**: Full support for Nostr Wallet Connect (NWC)
  - Human-to-agent payments
  - Agent-to-agent payments
  - Agent-to-tool payments

### Agent Frameworks
- **[Agno](https://docs.agno.com/introduction)**
- **[DSPy](https://dspy.ai/)**
- **[LangGraph](https://www.langchain.com/langgraph)**
- **[PydanticAI](https://ai.pydantic.dev/)**
- **[Google ADK](https://google.github.io/adk-docs/)**
- **[OpenAI](https://openai.github.io/openai-agents-python/)**
- **Bring Your Own Agent**

### MCP (Model Context Protocol) Support
- Nostr MCP Server for serving tools over Nostr
- Nostr MCP Client for discovering and calling remote tools

### A2A (Agent-to-Agent) Support
- Direct message handling between agents
- Discover agents using Nostr metadata

### RAG (Retrieval-Augmented Generation)
- Query and process Nostr events
- Context-aware response generation
- Event filtering

## Installation

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) recommended (or `pip`)

### Install from PyPI
```bash
uv add agentstr-sdk[all]
```

### Install from source
```bash
git clone https://github.com/agentstr/agentstr-sdk.git
cd agentstr-sdk
uv sync --all-extras
```

## Quick Start

### Environment Setup
Copy the [examples/.env.sample](examples/.env.sample) file to `examples/.env` and fill in the environment variables.

## Examples

The [examples/](examples/) directory contains various implementation examples:

- [nostr_dspy_agent.py](examples/nostr_dspy_agent.py): A DSPy agent connected to Nostr MCP
- [nostr_langgraph_agent.py](examples/nostr_langgraph_agent.py): A LangGraph agent connected to Nostr MCP
- [nostr_agno_agent.py](examples/nostr_agno_agent.py): An Agno agent connected to Nostr MCP
- [nostr_google_agent.py](examples/nostr_google_agent.py): A Google ADK agent connected to Nostr MCP
- [nostr_openai_agent.py](examples/nostr_openai_agent.py): An OpenAI agent connected to Nostr MCP
- [nostr_pydantic_agent.py](examples/nostr_pydantic_agent.py): A PydanticAI agent connected to Nostr MCP
- [mcp_server.py](examples/mcp_server.py): Nostr MCP server implementation
- [mcp_client.py](examples/mcp_client.py): Nostr MCP client example
- [chat_with_agents.py](examples/chat_with_agents.py): Send a direct message to an agent
- [tool_discovery.py](examples/tool_discovery.py): Tool discovery and usage
- [rag.py](examples/rag.py): Retrieval-augmented generation example

To run an example:
```bash
uv run examples/nostr_dspy_agent.py
```

### Security Notes
- Never commit your private keys or sensitive information to version control
- Use environment variables or a secure secret management system
- The `.env.sample` file shows the required configuration structure

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
