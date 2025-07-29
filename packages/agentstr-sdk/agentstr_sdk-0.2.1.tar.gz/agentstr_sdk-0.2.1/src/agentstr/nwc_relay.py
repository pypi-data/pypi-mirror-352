
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


BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


def encrypt(privkey, pubkey, plaintext):
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


def decrypt(privkey, pubkey, ciphertext):
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


def process_nwc_string(string):
    if (string[0:22] != "nostr+walletconnect://"):
        print('Your pairing string was invalid, try one that starts with this: nostr+walletconnect://')
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
    event = Event(**event)
    event.sign(private_key)
    return event


class NWCRelay(object):
    def __init__(self, nwc_str: str):
        self.nwc_info = process_nwc_string(nwc_str)
        self.event_relay = EventRelay(relay=self.nwc_info["relay"], private_key=PrivateKey.from_hex(self.nwc_info["app_privkey"]))
    
    async def get_response(self, event_id: str) -> Event | None:
        filters = Filters(
            event_refs=[event_id],
            pubkey_refs=[self.nwc_info["app_pubkey"]],
            kinds=[23195],
            limit=1
        )
        for i in range(5):
            event = await self.event_relay.get_event(filters=filters, timeout=5, close_on_eose=True)
            if event:
                return event
            await asyncio.sleep(0)
        return None

    async def make_invoice(self, amount: int, description: str) -> Event | None:
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
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj['result']['invoice']

    async def check_invoice(self, invoice=None, payment_hash=None):
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
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj

    async def did_payment_succeed(self, invoice):
        invoice_info = await self.check_invoice(invoice=invoice)
        if (invoice_info and not ("error" in invoice_info) and ("result" in invoice_info) and (
                "preimage" in invoice_info["result"])):
            return invoice_info.get("result", {}).get("settled_at") or 0 > 0
        return False

    async def try_pay_invoice(self, invoice, amount=None):
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

    async def get_info(self):
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
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj

    async def list_transactions(self, params={}):
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
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj

    async def get_balance(self):
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
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj

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
                        print(f"Error in callback: {e}")
                        raise e
                break
            if time.time() - start_time > timeout:
                break
            await asyncio.sleep(interval)
        if not success:
            if unsuccess_callback:
                await unsuccess_callback()