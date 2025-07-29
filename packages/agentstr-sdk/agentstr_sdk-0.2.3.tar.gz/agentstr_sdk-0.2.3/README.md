# Agentstr SDK

[![Documentation](https://img.shields.io/badge/docs-online-blue.svg)](https://agentstr.com/docs)
[![Usage Examples](https://img.shields.io/badge/examples-online-green.svg)](https://agentstr.com/usage)

## Overview

Agentstr SDK is a powerful toolkit for building agentic applications on the Nostr protocol. It integrates MCP (Model Context Protocol) and A2A (Agent-to-Agent) functionality with Nostr and the Lightning Network.

## Core Features

### Nostr Integration
- 📡 **NostrClient**: Core client for Nostr relay interactions
  - Event handling and management
  - Direct messaging
  - Metadata operations

### MCP Functionality
- 🛠️ **NostrMCPServer**: Tool server with payment support
  - Expose functions as tools
  - Optional satoshi payments via NWC
  - Tool discovery and registration

- 🔍 **NostrMCPClient**: Tool client with payment handling
  - Discover and call tools
  - Automatic payment processing

### AI & RAG
- 🤖 **NostrAgentServer**: Agent integration server
  - External agent communication
  - Direct message processing
  - Payment support for agent services

- 📚 **NostrRAG**: Retrieval-Augmented Generation
  - Query Nostr events
  - Context-aware responses
  - Event filtering and processing

### Payment Integration
- 💰 **NWCClient**: Nostr Wallet Connect
  - Payment processing and management
  - Invoice creation and handling
  - Payment verification

## Getting Started

### Check out our [Usage Guide](https://agentstr.com/usage) for detailed examples and tutorials.

## Quick Start Example
To demonstrate how to use the Agentstr SDK, here's an example of setting up an MCP server with mathematical tools and a client to call them:

### Installation

```bash
pip install agentstr-sdk
```

### MCP Server
```python
from agentstr import NostrMCPServer

# Define relays and private key
relays   = ['wss://some.relay.io']
private_key = 'nsec...'

# Define tools
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# Define the server
server = NostrMCPServer("Math MCP Server", relays=relays, private_key=private_key)

# Add tools
server.add_tool(add)
server.add_tool(multiply, name="multiply", description="Multiply two numbers")

# Start the server
server.start()
```

### MCP Client
```python
from agentstr import NostrMCPClient

# Define relays and private key
relays = ['wss://some.relay.io']
private_key = 'nsec...'

# Define MCP server public key
server_public_key = 'npub...'

# Initialize the client
mcp_client = NostrMCPClient(mcp_pubkey=server_public_key, relays=relays, private_key=private_key)

# List available tools
tools = mcp_client.list_tools()
print(f'Found tools: {json.dumps(tools, indent=4)}')

# Call a tool
result = mcp_client.call_tool("multiply", {"a": 69, "b": 420})
print(f'The result of 69 * 420 is: {result["content"][-1]["text"]}')
```

For more examples, see the [examples](examples) directory.

### Notes
+ **Environment Variables**: Do not hardcode Nostr private keys or NWC connection strings in your code. Use environment variables or some other secure method to store these values.
+ **Payment Handling**: Tools or agent interactions requiring satoshis use NWC for invoice creation and payment verification.
+ **Threading**: The SDK uses threading for asynchronous operations, such as listening for messages or monitoring payments.
