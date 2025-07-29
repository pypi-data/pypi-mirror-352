import asyncio
import json
import time
from typing import Any, List
from pynostr.utils import get_public_key
from agentstr.nostr_client import NostrClient


class NostrMCPClient:
    """A client for interacting with a Model Context Protocol (MCP) server on Nostr.

    This client discovers tools available on an MCP server and allows calling them,
    handling any required payments via Nostr Wallet Connect (NWC).

    Attributes:
        client (NostrClient): Nostr client for communication.
        mcp_pubkey (str): Public key of the MCP server.
        tool_to_sats_map (dict): Mapping of tool names to required satoshis.
    """
    def __init__(self, mcp_pubkey: str, nostr_client: NostrClient = None,
                 relays: List[str] = None, private_key: str = None, nwc_str: str = None):
        """Initialize the MCP client.

        Args:
            mcp_pubkey: Public key of the MCP server to interact with.
            nostr_client: Existing NostrClient instance (optional).
            relays: List of Nostr relay URLs (if no client provided).
            private_key: Nostr private key (if no client provided).
            nwc_str: Nostr Wallet Connect string for payments (optional).
        """
        self.client = nostr_client or NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str)
        self.mcp_pubkey = get_public_key(mcp_pubkey).hex()
        self.tool_to_sats_map = {}

    async def list_tools(self) -> dict[str, Any] | None:
        """Retrieve the list of available tools from the MCP server.

        Returns:
            Dictionary of tools with their metadata, or None if not found.
        """
        metadata = await self.client.get_metadata_for_pubkey(self.mcp_pubkey)
        tools = json.loads(metadata.about)
        for tool in tools['tools']:
            self.tool_to_sats_map[tool['name']] = tool['satoshis']
        return tools

    async def call_tool(self, name: str, arguments: dict[str, Any], timeout: int = 60) -> dict[str, Any] | None:
        """Call a tool on the MCP server with provided arguments.

        Args:
            name: Name of the tool to call.
            arguments: Dictionary of arguments for the tool.
            timeout: Timeout in seconds for receiving a response.

        Returns:
            Response dictionary from the server, or None if no response.
        """
        response = await self.client.send_direct_message_and_receive_response(self.mcp_pubkey, json.dumps({
            'action': 'call_tool', 'tool_name': name, 'arguments': arguments
        }), timeout=timeout)

        if response is None:
            print('Tool call returned None')
            return None

        message = response.message
        timestamp = int(time.time())

        print(f'MCP Client received message: {message}')
        if isinstance(message, str) and message.startswith('lnbc'):
            invoice = message.strip()
            print(f'Paying invoice: {invoice}')
            await self.client.nwc_relay.try_pay_invoice(invoice=invoice, amount=self.tool_to_sats_map[name])
            response = await self.client.receive_direct_message(self.mcp_pubkey, timestamp=timestamp, timeout=timeout) 

        if response:
            print(f'MCP Client received response.message: {response.message}')
            return json.loads(response.message)
        return None

