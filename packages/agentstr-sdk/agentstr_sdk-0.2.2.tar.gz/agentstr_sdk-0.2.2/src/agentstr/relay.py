import json
import uuid
import time
import asyncio
import threading
from typing import List, Callable
from expiringdict import ExpiringDict
from pydantic import BaseModel
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.utils import get_public_key, get_timestamp
from pynostr.event import Event, EventKind
from pynostr.filters import Filters
from pynostr.key import PrivateKey, PublicKey
from websockets.asyncio.client import connect 
from agentstr.logger import get_logger

logger = get_logger(__name__)


class DecryptedMessage(BaseModel):
    """A decrypted message from a Nostr relay."""
    event: Event
    message: str


class EventRelay(object):
    """Handles communication with a single Nostr relay.
    
    Args:
        relay: WebSocket URL of the Nostr relay
        private_key: Private key for signing events
        public_key: Optional public key (derived from private_key if not provided)
    """
    def __init__(self, relay: str, private_key: PrivateKey, public_key: PublicKey = None):
        self.relay = relay
        self.private_key = private_key
        self.public_key = public_key if public_key else (self.private_key.public_key if self.private_key else None)


    async def get_events(self, filters: Filters, limit: int = 10, timeout: int = 30, close_on_eose: bool = True) -> List[Event]:
        """Fetch events matching the given filters from this relay.
        
        Returns up to `limit` events that match the filters, or times out after `timeout` seconds.
        """
        limit = filters.limit if filters.limit else limit
        sid = uuid.uuid4().hex
        subscription = ["REQ", sid, filters.to_dict()]
        events = []
        t0 = time.time()
        time_remaining = timeout
        async with connect(self.relay) as ws:
            logger.debug(f'Sending subscription: {json.dumps(subscription)}')
            await ws.send(json.dumps(subscription))
            t0 = time.time()
            found = 0
            await asyncio.sleep(0)
            try:
                while time.time() < t0 + timeout and found < limit: 
                    response = await asyncio.wait_for(ws.recv(), timeout=time_remaining)     
                    response = json.loads(response)
                    logger.debug(f"Received full message in get_events: {response}")
                    if (len(response) > 2):
                        found += 1
                        logger.debug(f"Received message {found} in get_event: {response[2]}")
                        events.append(Event.from_dict(response[2]))
                    else:
                        if response[0] == 'EOSE':
                            logger.debug('Received EOSE in get_events')
                            if close_on_eose:
                                logger.debug('Closing connection on EOSE.')
                                break
                        logger.warning(f"Invalid event: {response}")
                    await asyncio.sleep(0)
                    time_remaining = t0 + timeout - time.time()
                    if time_remaining <= 0:
                        raise asyncio.TimeoutError()
            except asyncio.TimeoutError:
                logger.warning('Timeout in get_events')
                pass
        return events

    async def get_event(self, filters: Filters, timeout: int = 30, close_on_eose: bool = True) -> Event | None:
        """Get a single event matching the filters or None if not found."""
        events = await self.get_events(filters, limit=1, timeout=timeout, close_on_eose=close_on_eose)
        if len(events) > 0:
            return events[0]
        else:
            return None

    async def send_event(self, event: Event):
        """Publish an event to this relay."""
        if not event.sig:
            event.sign(self.private_key.hex())
        message = event.to_message()
        async with connect(self.relay) as ws:
            logger.debug(f'Sending message: {message}')
            await ws.send(message)
            response = await ws.recv()
            logger.debug(f'Received send_event response: {response}')

    def decrypt_message(self, event: Event) -> DecryptedMessage | None:
        if event and event.has_pubkey_ref(self.public_key.hex()):
            rdm = EncryptedDirectMessage.from_event(event)
            rdm.decrypt(self.private_key.hex(), public_key_hex=event.pubkey)
            logger.debug(f"New dm received: {event.date_time()} {rdm.cleartext_content}")
            return DecryptedMessage(
                event=event,
                message=rdm.cleartext_content
            )
        return None

    async def send_message(self, message: str | dict, recipient_pubkey: str, event_ref: str = None) -> Event:
        recipient = get_public_key(recipient_pubkey)
        dm = EncryptedDirectMessage(reference_event_id=event_ref)
        
        if isinstance(message, dict):
            message = json.dumps(message)

        dm.encrypt(self.private_key.hex(), cleartext_content=message, recipient_pubkey=recipient.hex())
        dm_event = dm.to_event()
        await self.send_event(dm_event)
        return dm_event

    async def receive_message(self, author_pubkey: str, timestamp: int = None, timeout: int = 30) -> DecryptedMessage | None:
        """Wait for and return the next direct message from the specified author."""
        author = get_public_key(author_pubkey)
        authors = [author.hex()]
        filters = Filters(authors=authors, kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
                            pubkey_refs=[self.public_key.hex()], since=timestamp or get_timestamp(), limit=1)
        event = await self.get_event(filters, timeout, close_on_eose=False)
        if event:
            return self.decrypt_message(event)
        return None

    async def send_receive_message(self, message: str | dict, recipient_pubkey: str, timeout: int = 3, event_ref: str = None) -> DecryptedMessage | None:
        dm_event = await self.send_message(message, recipient_pubkey, event_ref)
        timestamp = dm_event.created_at
        return await self.receive_message(recipient_pubkey, timestamp, timeout)       

    async def event_listener(self, filters: Filters, callback: Callable[[Event], None], event_cache: ExpiringDict, lock: asyncio.Lock):
        """Continuously listen for events matching filters and call the callback for each one."""
        sid = uuid.uuid4().hex
        subscription = ["REQ", sid, filters.to_dict()]
        logger.debug(f'Sending note subscription: {json.dumps(subscription)}')
        async with connect(self.relay) as ws:
            await ws.send(json.dumps(subscription))
            while True:      
                response = await ws.recv()
                response = json.loads(response)
                if (len(response) > 2):
                    event = Event.from_dict(response[2])
                    logger.debug(f'Checking lock with event id: {event.id}')
                    async with lock:
                        if event.id in event_cache:
                            continue
                        event_cache[event.id] = True
                    await callback(event)
                await asyncio.sleep(0)

    async def direct_message_listener(self, filters: Filters, callback: Callable[[Event, str], None], event_cache: ExpiringDict, lock: asyncio.Lock):
        """Listen for direct messages and call the callback with decrypted content."""
        sid = uuid.uuid4().hex
        subscription = ["REQ", sid, filters.to_dict()]
        logger.debug(f'Sending DM subscription: {json.dumps(subscription)}')
        async with connect(self.relay) as ws:
            await ws.send(json.dumps(subscription))
            while True:      
                response = await ws.recv()
                response = json.loads(response)
                if (len(response) > 2):
                    logger.debug(f"Received message in direct_message_listener: {response[2]}")
                    event = Event.from_dict(response[2])
                    logger.debug(f'Checking lock with event id: {event.id}')
                    async with lock:
                        if event.id in event_cache:
                            continue
                        event_cache[event.id] = True
                    dm = self.decrypt_message(event)
                    if dm:
                        logger.debug(f"New dm received: {event.date_time()} {dm.message}")
                        await callback(dm.event, dm.message)
                await asyncio.sleep(0)