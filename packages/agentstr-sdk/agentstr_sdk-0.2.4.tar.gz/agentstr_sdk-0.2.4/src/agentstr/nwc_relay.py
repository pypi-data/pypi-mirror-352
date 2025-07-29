
"""Nostr Wallet Connect (NWC) relay implementation for handling payments."""

import json
import math
import time
import asyncio
from bolt11.decode import decode
from pynostr.event import Event
from pynostr.filters import Filters
from pynostr.key import PrivateKey
import base64
from secp256k1 import PublicKey
from Crypto import Random
from Crypto.Cipher import AES
from agentstr.relay import EventRelay
from agentstr.logger import get_logger

logger = get_logger(__name__)

# AES encryption constants
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


def encrypt(privkey: str, pubkey: str, plaintext: str) -> str:
    """Encrypt plaintext using ECDH shared secret.
    
    Returns:
        Base64-encoded ciphertext with IV as URL parameter
    """
    key = PublicKey(bytes.fromhex("02" + pubkey), True).tweak_mul(bytes.fromhex(privkey)).serialize().hex()[2:]
    key_bytes = 32
    key = bytes.fromhex(key)
    plaintext = pad(plaintext)
    plaintext = plaintext.encode("utf-8")
    assert len(key) == key_bytes

    # Choose a random, 16-byte IV.
    iv = Random.new().read(AES.block_size)

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CBC, iv)

    # Encrypt and return IV and ciphertext.
    ciphertext = aes.encrypt(plaintext)

    # Convert to base64
    cipher_b64 = base64.b64encode(ciphertext).decode('ascii')
    cipher_iv = base64.b64encode(iv).decode('ascii')

    return cipher_b64 + "?iv=" + cipher_iv


def decrypt(privkey: str, pubkey: str, ciphertext: str) -> str:
    """Decrypt ciphertext using ECDH shared secret.
    
    Args:
        ciphertext: Base64-encoded ciphertext with IV as URL parameter
    """
    key = PublicKey(bytes.fromhex("02" + pubkey), True).tweak_mul(bytes.fromhex(privkey)).serialize().hex()[2:]
    key_bytes = 32
    key = bytes.fromhex(key)
    (ciphertext, iv) = ciphertext.split("?iv=")
    ciphertext = base64.b64decode(ciphertext.encode('ascii'))
    iv = base64.b64decode(iv.encode('ascii'))
    assert len(key) == key_bytes

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt and return the plaintext.
    plaintext = aes.decrypt(ciphertext).decode('ascii')
    plaintext = unpad(plaintext)
    return plaintext


def process_nwc_string(string: str) -> dict:
    """Parse Nostr Wallet Connect connection string into its components.
    
    Returns:
        Dictionary containing connection parameters
    """
    if (string[0:22] != "nostr+walletconnect://"):
        logger.error('Your pairing string was invalid, try one that starts with this: nostr+walletconnect://')
        return
    string = string[22:]
    arr = string.split("&")
    item = arr[0].split("?")
    del arr[0]
    arr.insert(0, item[0])
    arr.insert(1, item[1])
    arr[0] = "wallet_pubkey=" + arr[0]
    arr2 = []
    obj = {}
    for item in arr:
        item = item.split("=")
        arr2.append(item[0])
        arr2.append(item[1])
    for index, item in enumerate(arr2):
        if (item == "secret"):
            arr2[index] = "app_privkey"
    for index, item in enumerate(arr2):
        if (index % 2):
            obj[arr2[index - 1]] = item
    obj["app_pubkey"] = PrivateKey.from_hex(obj["app_privkey"]).public_key.hex()
    return obj


def get_signed_event(event: dict, private_key: str) -> Event:
    """Create and sign a Nostr event with the given private key."""
    event = Event(**event)
    event.sign(private_key)
    return event


class NWCRelay:
    """Client for interacting with Nostr Wallet Connect (NWC) relays.
    
    Handles encrypted communication with wallet services over the Nostr network.
    """
    def __init__(self, nwc_connection_string: str, relay: str = None):
        """Initialize NWC client with connection string and optional relay URL.
        
        Args:
            nwc_connection_string: NWC connection string (starts with 'nostr+walletconnect://')
            relay: Optional relay URL override
        """
        logger.info(f'Initializing NWCRelay with connection string: {nwc_connection_string[:10]}...')
        try:
            self.nwc_info = process_nwc_string(nwc_connection_string)
            if relay is None:
                relay = self.nwc_info['relay']
            logger.debug(f'Using relay: {relay}')
            self.event_relay = EventRelay(relay, private_key=PrivateKey.from_hex(self.nwc_info["app_privkey"]))
            logger.info('NWCRelay initialized successfully')
        except Exception as e:
            logger.critical(f'Failed to initialize NWCRelay: {str(e)}', exc_info=True)
            raise

    async def get_response(self, event_id: str) -> Event | None:
        """Get response for a specific event ID."""
        filters = Filters(
            event_refs=[event_id],
            pubkey_refs=[self.nwc_info["app_pubkey"]],
            kinds=[23195],
            limit=1
        )
        for i in range(10):
            event = await self.event_relay.get_event(filters=filters, timeout=5, close_on_eose=True)
            if event:
                return event
            await asyncio.sleep(0)
        return None

    async def make_invoice(self, amount: int, description: str) -> Event | None:
        """Generate a new payment request.
        
        Returns:
            Dictionary containing invoice details
        """
        msg = json.dumps({
            "method": "make_invoice",
            "params": {
                "amount": amount * 1000,
                "description": description,
            } if amount else {
                "description": description,
            }
        })
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg)
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        await self.event_relay.send_event(event)
        response = await self.get_response(event.id)
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj['result']['invoice']

    async def check_invoice(self, invoice: str = None, payment_hash: str = None) -> dict:
        """Check the status of an invoice by its payment hash or invoice string."""
        if invoice is None and payment_hash is None:
            raise ValueError("Either 'invoice' or 'payment_hash' must be provided")

        params = {}
        if invoice is not None:
            params["invoice"] = invoice
        if payment_hash is not None:
            params["payment_hash"] = payment_hash

        msg = json.dumps({
            "method": "lookup_invoice",
            "params": params
        })
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg);
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        eid = event.id
        await self.event_relay.send_event(event)
        response = await self.get_response(eid)
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj

    async def did_payment_succeed(self, invoice: str) -> bool:
        """Check if a payment was successful.
        
        Returns:
            True if payment was successful, False otherwise
        """
        invoice_info = await self.check_invoice(invoice=invoice)
        if (invoice_info and not ("error" in invoice_info) and ("result" in invoice_info) and (
                "preimage" in invoice_info["result"])):
            return invoice_info.get("result", {}).get("settled_at") or 0 > 0
        return False

    async def try_pay_invoice(self, invoice: str, amount: int = None) -> dict:
        """Attempt to pay a BOLT11 invoice.
        
        Returns:
            Dictionary with payment status and details
        """
        decoded = decode(invoice)
        if decoded.amount_msat and amount:
            if decoded.amount_msat != amount * 1000:  # convert to msats
                raise RuntimeError(f'Amount in invoice [{decoded.amount_msat}] does not match amount provided [{amount}]')
        elif not decoded.amount_msat and not amount:
            raise RuntimeError('No amount provided in invoice and no amount provided to pay')
        msg = {
            "method": "pay_invoice",
            "params": {
                "invoice": invoice,
            }
        }
        if (amount): msg["params"]["amount"] = amount * 1000
        msg = json.dumps(msg)
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg);
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        await self.event_relay.send_event(event)

    async def get_info(self) -> dict:
        """Get wallet service information and capabilities."""
        msg = {
            "method": "get_info"
        }
        msg = json.dumps(msg)
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg);
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        await self.event_relay.send_event(event)
        response = await self.get_response(event.id)
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj

    async def list_transactions(self, params: dict = None) -> list[dict]:
        """List recent transactions matching the given parameters."""
        if params is None:
            params = {}
        msg = {
            "method": "list_transactions",
            "params": params
        }
        msg = json.dumps(msg)
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg);
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        await self.event_relay.send_event(event)
        response = await self.get_response(event.id)
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj.get('result', {}).get('transactions', [])

    async def get_balance(self) -> int | None:
        """Get current wallet balance."""
        msg = {
            "method": "get_balance"
        }
        msg = json.dumps(msg)
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg);
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        await self.event_relay.send_event(event)
        response = await self.get_response(event.id)
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj.get('result', {}).get('balance')

    async def on_payment_success(self, invoice: str, callback=None, unsuccess_callback=None, timeout: int = 300, interval: int = 2):
        """
        Listen for payment success for a given invoice.

        This method continuously checks for payment success until either the payment
        is confirmed or the timeout is reached.

        Args:
            invoice (str): The BOLT11 invoice string to listen for.
            callback (callable, optional): A function to call when payment succeeds.
            unsuccess_callback (callable, optional): A function to call if payment fails.
            timeout (int, optional): Maximum time to wait in seconds (default: 300).
            interval (int, optional): Time between checks in seconds (default: 2).

        Raises:
            Exception: If the callback function raises an exception.
        """
        start_time = time.time()
        success = False
        while True:
            if await self.did_payment_succeed(invoice):
                success = True
                if callback:
                    try:
                        await callback()
                    except Exception as e:
                        logger.error(f"Error in callback: {e}", exc_info=True)
                        raise e
                break
            if time.time() - start_time > timeout:
                break
            await asyncio.sleep(interval)
        if not success:
            if unsuccess_callback:
                await unsuccess_callback()