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
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Overview

Agentstr SDK is a powerful toolkit for building agentic applications on the Nostr protocol. It provides seamless integration with various AI agent frameworks and enables decentralized agent-to-agent communication using Nostr relays.

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
- **DSPy**
- **LangGraph**
- **Agno**
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
Copy the `examples/.env.sample` file to `.env` and fill in the environment variables.

## Examples

The `examples/` directory contains various implementation examples:

- `dspy_agent.py`: DSPy-powered agent with tool usage
- `langgraph_agent.py`: Agent workflow with LangGraph
- `agno_agent.py`: Simple agent implementation
- `dm_agents.py`: Direct message handling between agents
- `mcp_server.py`: MCP server implementation (lightning-enabled)
- `mcp_client.py`: MCP client example (lightning-enabled)
- `tool_discovery.py`: Tool discovery and usage
- `rag.py`: Retrieval-augmented generation example

To run an example:
```bash
uv run examples/dspy_agent.py
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
