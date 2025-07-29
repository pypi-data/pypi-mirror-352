import asyncio
from typing import Any, List, Callable, Optional
from pynostr.event import Event
from agentstr.a2a import AgentCard, ChatInput, agent_router_v2, RouterResponse
from agentstr.nostr_client import NostrClient
from pydantic import BaseModel
from agentstr.logger import get_logger

logger = get_logger(__name__)


class NoteFilters(BaseModel):
    """Filters for filtering Nostr notes/events.
    
    Attributes:
        nostr_pubkeys: Filter by specific public keys
        nostr_tags: Filter by specific tags
        following_only: Only show notes from followed users (not implemented)
    """
    nostr_pubkeys: list[str] | None = None
    nostr_tags: list[str] | None = None
    following_only: bool = False


class NostrAgentServer:
    """Server that integrates an external agent with the Nostr network.
    
    Handles direct messages and optional payments, routing them to an external agent.
    """
    def __init__(self, 
                 nostr_client: NostrClient = None,
                 relays: List[str] = None, 
                 private_key: str = None, 
                 nwc_str: str = None, 
                 agent_info: AgentCard = None, 
                 agent_callable: Callable[[ChatInput], str] = None,
                 note_filters: NoteFilters = None, 
                 router_llm: Any = None):
        """Initialize the agent server. If agent_info and agent_callable are provided, agent_url, chat_url_path, and info_url_path are ignored.

        Args:
            nostr_client: Existing NostrClient instance (optional).
            relays: List of Nostr relay URLs (if no client provided).
            private_key: Nostr private key (if no client provided).
            nwc_str: Nostr Wallet Connect string for payments (optional).
            agent_info: Agent information (optional).
            agent_callable: Callable to handle agent responses.
            note_filters: Filters for listening to Nostr notes (optional).
            router_llm: LLM to use for routing (optional).
        """
        self.client = nostr_client or NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str)
        self.agent_info = agent_info
        self.agent_callable = agent_callable
        self.note_filters = note_filters
        self.router_llm = router_llm

    async def chat(self, message: str, thread_id: Optional[str] = None) -> Any:
        """Send a message to the agent and retrieve the response.

        Args:
            message: The message to send to the agent.
            thread_id: Optional thread ID for conversation context.

        Returns:
            Response from the agent, or an error message.
        """
        return await self.agent_callable(ChatInput(messages=[message], thread_id=thread_id))

    async def _handle_paid_invoice(self, event: Event, message: str, invoice: str, router_response: RouterResponse = None):
        """Handle a paid invoice."""
        if router_response:
            skills_used = ', '.join(router_response.skills_used)
            message = f'''I'd like to follow up on our previous exchange:

Your Request:
{message}

Your Response:
{router_response.user_message}

Could you please proceed with the next steps or provide an update on this matter?

Only use the following tools: [{skills_used}]
'''

        print(f'Handling paid invoice')

        async def on_success():
            logger.info(f"Payment succeeded for {self.agent_info.name}")
            result = await self.chat(message, thread_id=event.pubkey)
            response = str(result)
            logger.debug(f'On success response: {response}')
            await self.client.send_direct_message(event.pubkey, response)


        async def on_failure():
            response = "Payment failed. Please try again."
            logger.error(f"On failure response: {response}")
            await self.client.send_direct_message(event.pubkey, response)

        await self.client.nwc_relay.on_payment_success(
            invoice=invoice,
            callback=on_success,
            timeout=900,
            unsuccess_callback=on_failure
        )


    async def _direct_message_callback(self, event: Event, message: str):
        """Handle incoming direct messages for agent interaction.

        Args:
            event: The Nostr event containing the message.
            message: The message content.
        """
        if message.strip().startswith('{') or message.strip().startswith('['):
            logger.debug('Ignoring JSON messages')
            return
        elif message.strip().startswith('lnbc') and ' ' not in message.strip():
            logger.debug('Ignoring lightning invoices')
            return
        message = message.strip()
        invoice = None
        router_response = None
        logger.debug(f"Request: {message}")
        try:
            response = None
            cost_sats = None
            if self.router_llm:
                router_response = await agent_router_v2(message, self.agent_info, self.router_llm, thread_id=event.pubkey)
                response = router_response.user_message
                if router_response.can_handle:
                    cost_sats = router_response.cost_sats
                else:
                    await self.client.send_direct_message(event.pubkey, response)
                    return

            cost_sats = cost_sats or (self.agent_info.satoshis if self.agent_info else 0)
            if cost_sats > 0:
                invoice = await self.client.nwc_relay.make_invoice(amount=cost_sats, description=f"Payment for {self.agent_info.name}")
                if response is not None:
                    response = f'{response}\n\nPlease pay {cost_sats} sats: {invoice}'
                else:
                    response = invoice
            else:
                result = await self.chat(message, thread_id=event.pubkey)
                response = str(result)
        except Exception as e:
            response = f'Error in direct message callback: {e}'
            
        logger.debug(f'Response: {response}')
        tasks = []
        tasks.append(self.client.send_direct_message(event.pubkey, response))
        if invoice:
            tasks.append(self._handle_paid_invoice(event, message, invoice, router_response))
        await asyncio.gather(*tasks)


    async def _note_callback(self, event: Event):
        """Handle incoming notes that match the filters.
        
        Args:
            event: The Nostr event containing the note.
        """
        try:
            content = event.content
            logger.info(f"Received note from {event.pubkey}: {content}")
            
            router_response = await agent_router_v2(content, self.agent_info, self.router_llm, thread_id=event.pubkey)
            logger.debug(f"Router response: {router_response.model_dump()}")

            if router_response.can_handle:
                # Formulate and send direct message to the user
                response = router_response.user_message
                tasks = []
                if router_response.cost_sats > 0:
                    invoice = await self.client.nwc_relay.make_invoice(amount=router_response.cost_sats, description=f"Payment to {self.agent_info.name}")
                    response = f'{response}\n\nPlease pay {router_response.cost_sats} sats: {invoice}'
                    tasks.append(self._handle_paid_invoice(event, content, invoice, router_response))

                tasks.append(self.client.send_direct_message(event.pubkey, response, event_ref=event.id))
                await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error processing note: {e}", exc_info=True)

    async def start(self):
        """Start the agent server, updating metadata and listening for direct messages and notes."""
        logger.info(f'Updating metadata for {self.client.public_key.bech32()}')
        if self.agent_info:
            await self.client.update_metadata(
                name='agent_server',
                display_name=self.agent_info.name,
                about=self.agent_info.model_dump_json()
            )
        
        tasks = []
        # Start note listener if filters are provided (in new thread)
        if self.note_filters is not None:
            logger.info(f'Starting note listener with filters: {self.note_filters.model_dump()}')
            tasks.append(
                self.client.note_listener(
                    callback=self._note_callback,
                    pubkeys=self.note_filters.nostr_pubkeys,
                    tags=self.note_filters.nostr_tags,
                    followers_only=self.note_filters.followers_only,
                    following_only=self.note_filters.following_only
                )
            )
        
        # Start direct message listener
        logger.info(f'Starting message listener for {self.client.public_key.bech32()}')
        
        await self.client.direct_message_listener(callback=self._direct_message_callback)
        
