import asyncio
import json
import time
from typing import List, Callable
from expiringdict import ExpiringDict
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.event import Event
from pynostr.filters import Filters
from pynostr.key import PrivateKey
from pynostr.utils import get_public_key
from agentstr.relay import DecryptedMessage, EventRelay


class RelayManager(object):
    def __init__(self, relays: List[str], private_key: PrivateKey):
        self._relays = relays
        self.private_key = private_key
        self.public_key = self.private_key.public_key if self.private_key else None
        
    @property
    def relays(self):
        return [EventRelay(relay, self.private_key, self.public_key) for relay in self._relays]
    
    async def get_events(self, filters: Filters, limit: int = 10, timeout: int = 30, close_on_eose: bool = True) -> List[Event]:
        limit = filters.limit if filters.limit else limit
        event_id_map = {}
        result = None
        t0 = time.time()
        tasks = []
        for relay in self.relays:   
            tasks.append(asyncio.create_task(relay.get_events(filters, limit, timeout, close_on_eose)))
        for done in asyncio.as_completed(tasks):
            result = await done
            if result and len(result) >= limit:
                break
            for event in result:
                if event.id in event_id_map:
                    continue
                event_id_map[event.id] = event
                if len(event_id_map) >= limit:
                    result = list(event_id_map.values())  
                    break
            if timeout < time.time() - t0:
                break            
        if not result:
            result = list(event_id_map.values())  
        return result

    async def get_event(self, filters: Filters, timeout: int = 30, close_on_eose: bool = True) -> Event:
        result = await self.get_events(filters, limit=1, timeout=timeout, close_on_eose=close_on_eose)
        if result and len(result) > 0:
            return result[0]
        return None

    async def send_event(self, event: Event) -> Event:
        tasks = []
        event.created_at = int(time.time())
        event.compute_id()
        event.sign(self.private_key.hex())
        for relay in self.relays:   
            tasks.append(asyncio.create_task(relay.send_event(event)))
        await asyncio.gather(*tasks)

    def encrypt_message(self, message: str | dict, recipient_pubkey: str, event_ref: str = None) -> Event:
        recipient = get_public_key(recipient_pubkey)
        dm = EncryptedDirectMessage(reference_event_id=event_ref)
        
        if isinstance(message, dict):
            message = json.dumps(message)

        dm.encrypt(self.private_key.hex(), cleartext_content=message, recipient_pubkey=recipient.hex())
        event = dm.to_event()
        event.created_at = int(time.time())
        event.compute_id()
        event.sign(self.private_key.hex())
        return event

    async def send_message(self, message: str | dict, recipient_pubkey: str, event_ref: str = None) -> Event:
        tasks = []
        event = self.encrypt_message(message, recipient_pubkey, event_ref)
        #print(f'Sending message: {event.to_dict()}')
        for relay in self.relays:   
            tasks.append(asyncio.create_task(relay.send_event(event)))
        await asyncio.gather(*tasks)
        return event

    async def receive_message(self, author_pubkey: str, timestamp: int = None, timeout: int = 30) -> DecryptedMessage | None:
        tasks = []
        t0 = time.time()
        for relay in self.relays:   
            tasks.append(asyncio.create_task(relay.receive_message(author_pubkey, timestamp, timeout)))
        for task in asyncio.as_completed(tasks):
            result = await task
            #print(f'Received message in receive_message: {result}')
            if result:
                return result
            if timeout < time.time() - t0:
                break            
        return None

    async def send_receive_message(self, message: str | dict, recipient_pubkey: str, timeout: int = 3, event_ref: str = None) -> DecryptedMessage | None:
        dm_event = await self.send_message(message, recipient_pubkey, event_ref)
        timestamp = dm_event.created_at
        #print(f'Sent receive DM event: {dm_event.to_dict()}')
        return await self.receive_message(recipient_pubkey, timestamp, timeout)

    async def event_listener(self, filters: Filters, callback: Callable[[Event], None]):
        event_cache = ExpiringDict(max_len=1000, max_age_seconds=300)
        lock = asyncio.Lock()
        tasks = []
        for relay in self.relays:   
            tasks.append(asyncio.create_task(relay.event_listener(filters, callback, event_cache, lock)))
        await asyncio.gather(*tasks)

    async def direct_message_listener(self, filters: Filters, callback: Callable[[Event, str], None]):
        event_cache = ExpiringDict(max_len=1000, max_age_seconds=300)
        lock = asyncio.Lock()
        tasks = []
        for relay in self.relays:   
            tasks.append(asyncio.create_task(relay.direct_message_listener(filters, callback, event_cache, lock)))
        await asyncio.gather(*tasks)

    async def get_following(self, pubkey: str = None) -> list[str]:
        pubkey = get_public_key(pubkey).hex() if pubkey else self.public_key.hex()
        filters = Filters(authors=[pubkey], kinds=[3], limit=1)
        event = await self.get_event(filters)
        if event:
            return [tag[1] for tag in event.tags if tag[0] == 'p']
        return []