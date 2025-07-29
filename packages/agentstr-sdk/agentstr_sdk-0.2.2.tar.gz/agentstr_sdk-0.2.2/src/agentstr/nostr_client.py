"""Nostr client implementation for interacting with the Nostr network."""

import time
from typing import List, Any, Optional, Callable
from pynostr.key import PrivateKey
from pynostr.event import Event, EventKind
from pynostr.filters import Filters
from pynostr.metadata import Metadata
from pynostr.utils import get_public_key, get_timestamp
from agentstr.nwc_relay import NWCRelay
from agentstr.relay import DecryptedMessage
from agentstr.relay_manager import RelayManager
from agentstr.logger import get_logger

logger = get_logger(__name__)


class NostrClient:
    """A client for interacting with the Nostr protocol, handling events, direct messages, and metadata.

    This class provides methods to connect to Nostr relays, send and receive direct messages,
    manage metadata, and read posts by tags. It integrates with Nostr Wallet Connect (NWC)
    for payment processing if provided.
    """
    def __init__(self, relays: List[str], private_key: str = None, nwc_str: str = None):
        """Initialize the NostrClient.

        Args:
            relays: List of Nostr relay URLs to connect to.
            private_key: Nostr private key in 'nsec' format.
            nwc_str: Nostr Wallet Connect string for payment processing (optional).
        """
        logger.info('Initializing NostrClient')
        try:
            self.relays = relays
            logger.debug(f'Using relays: {relays}')
            
            if private_key:
                self.private_key = PrivateKey.from_nsec(private_key)
                self.public_key = self.private_key.public_key
                logger.debug(f'Initialized with public key: {self.public_key.bech32()}')
            else:
                self.private_key = None
                self.public_key = None
                logger.warning('No private key provided, client will be in read-only mode')
                
            self.nwc_str = nwc_str
            if nwc_str:
                logger.info('Nostr Wallet Connect (NWC) is enabled')
            else:
                logger.info('Nostr Wallet Connect (NWC) is not configured')
                
        except Exception as e:
            logger.critical(f'Failed to initialize NostrClient: {str(e)}', exc_info=True)
            raise

    @property
    def relay_manager(self) -> RelayManager:
        return RelayManager(self.relays, self.private_key)

    @property
    def nwc_relay(self) -> NWCRelay | None:
        """NWCRelay instance if NWC is configured."""
        return NWCRelay(self.nwc_str) if self.nwc_str else None

    def sign(self, event: Event) -> Event:
        """Sign an event with the client's private key.

        Args:
            event: The Nostr event to sign.

        Returns:
            The signed event.
        """
        event.sign(self.private_key.hex())
        return event

    async def read_posts_by_tag(self, tag: str = None, tags: List[str] = None, limit: int = 10) -> List[Event]:
        """Read posts containing a specific tag from Nostr relays.

        Args:
            tag: The tag to filter posts by.
            tags: List of tags to filter posts by.
            limit: Maximum number of posts to retrieve.

        Returns:
            List of Events.
        """
        filters = Filters(limit=limit, kinds=[EventKind.TEXT_NOTE])
        filters.add_arbitrary_tag("t", tags or [tag])

        return await self.relay_manager.get_events(filters)

    async def get_metadata_for_pubkey(self, public_key: str | PrivateKey = None) -> Optional[Metadata]:
        """Fetch metadata for a public key (or self if none provided)."""
        public_key = get_public_key(public_key if isinstance(public_key, str) else public_key.hex()) if public_key else self.public_key
        filters = Filters(kinds=[EventKind.SET_METADATA], authors=[public_key.hex()], limit=1)
        event = await self.relay_manager.get_event(filters)
        if event:
            return Metadata.from_event(event)
        return None

    async def update_metadata(self, name: Optional[str] = None, about: Optional[str] = None,
                       nip05: Optional[str] = None, picture: Optional[str] = None,
                       banner: Optional[str] = None, lud16: Optional[str] = None,
                       lud06: Optional[str] = None, username: Optional[str] = None,
                       display_name: Optional[str] = None, website: Optional[str] = None):
        """Update the client's metadata on Nostr relays.

        Args:
            name: Nostr name.
            about: Description or bio.
            nip05: NIP-05 identifier.
            picture: Profile picture URL.
            banner: Banner image URL.
            lud16: Lightning address.
            lud06: LNURL.
            username: Username.
            display_name: Display name.
            website: Website URL.
        """
        previous_metadata = await self.get_metadata_for_pubkey(self.public_key)
        metadata = Metadata()
        if previous_metadata:
            metadata.set_metadata(previous_metadata.metadata_to_dict())
        if name:
            metadata.name = name
        if about:
            metadata.about = about
        if nip05:
            metadata.nip05 = nip05
        if picture:
            metadata.picture = picture
        if banner:
            metadata.banner = banner
        if lud16:
            metadata.lud16 = lud16
        if lud06:
            metadata.lud06 = lud06
        if username:
            metadata.username = username
        if display_name:
            metadata.display_name = display_name
        if website:
            metadata.website = website
        metadata.created_at = int(time.time())
        metadata.update()
        if previous_metadata and previous_metadata.content == metadata.content:
            print("No changes in metadata, skipping update.")
            return

        await self.relay_manager.send_event(metadata.to_event())

    async def send_direct_message(self, recipient_pubkey: str, message: str, event_ref: str = None) -> Event:
        """Send an encrypted direct message to a recipient.

        Args:
            recipient_pubkey: The recipient's public key in hex or bech32 format.
            message: The message content to send.
            event_ref: Optional event ID to reference in the message.

        Returns:
            The sent event.
        """
        logger.info(f'Sending direct message to {recipient_pubkey[:10]}...')
        logger.debug(f'Message content: {message[:100]}...')
        
        if not self.private_key:
            error_msg = "Private key is required to send messages"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            event = await self.relay_manager.send_message(
                message=message,
                recipient_pubkey=recipient_pubkey,
                event_ref=event_ref
            )
            logger.info(f'Successfully sent direct message with event ID: {event.id}')
            logger.debug(f'Full event: {event.to_dict()}')
            return event
            
        except Exception as e:
            logger.error(f'Failed to send direct message: {str(e)}', exc_info=True)
            raise

    async def receive_direct_message(self, recipient_pubkey: str, timestamp: int = None, timeout: int = 30) -> DecryptedMessage | None:
        """Wait for and return the next direct message from a recipient."""
        return await self.relay_manager.receive_message(recipient_pubkey, timestamp=timestamp, timeout=timeout)

    async def send_direct_message_and_receive_response(self, recipient_pubkey: str, message: str, timeout: int = 30, event_ref: str = None) -> DecryptedMessage:
        """Send an encrypted direct message to a recipient and wait for a response.

        Args:
            recipient_pubkey: The recipient's public key.
            message: The message content (string or dict, which will be JSON-encoded).
        """
        return await self.relay_manager.send_receive_message(message=message, recipient_pubkey=recipient_pubkey, timeout=timeout, event_ref=event_ref)

    async def note_listener(self, callback: Callable[[Event], Any], pubkeys: List[str] = None, 
                     tags: List[str] = None, following_only: bool = False, timestamp: int = None):
        """Listen for public notes matching the given filters.

        Args:
            callback: Function to handle received notes (takes Event as argument).
            pubkeys: List of pubkeys to filter notes from (hex or bech32 format).
            tags: List of tags to filter notes by.
            following_only: If True, only show notes from users the agent is following (optional).
            timestamp: Filter messages since this timestamp (optional).
        """

        authors = None
        if following_only:
            authors = await self.relay_manager.get_following()
        elif pubkeys:
            authors = [get_public_key(pk).hex() for pk in pubkeys]        
        filters = Filters(authors=authors, kinds=[EventKind.TEXT_NOTE],
                                since=timestamp or get_timestamp(), limit=10)
        if tags and len(tags) > 0:
            filters.add_arbitrary_tag("t", tags)

        await self.relay_manager.event_listener(filters, callback)

    async def direct_message_listener(self, callback: Callable[[Event, str], Any], recipient_pubkey: str = None, timestamp: int = None):
        """Listen for incoming encrypted direct messages.

        Args:
            callback: Function to handle received messages (takes Event and message content as args).
            recipient_pubkey: Filter messages from a specific public key (optional).
            timeout: Timeout for listening in seconds (0 for indefinite).
            timestamp: Filter messages since this timestamp (optional).
            close_after_first_message: Close subscription after receiving the first message.
        """
        authors = [get_public_key(recipient_pubkey).hex()] if recipient_pubkey else None
        filters = Filters(authors=authors, kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
                                      since=timestamp or get_timestamp(), pubkey_refs=[self.public_key.hex()],
                                      limit=10)
        
        await self.relay_manager.direct_message_listener(filters, callback)