import os
import dotenv
from agentstr.nwc_relay import NWCRelay

dotenv.load_dotenv()

nwc_relay = NWCRelay(os.getenv('TEST_NWC_CONN_STR'))
nwc_relay2 = NWCRelay(os.getenv('TEST_NWC_CONN_STR2'))


async def test_make_invoice():
    invoice = await nwc_relay.make_invoice(amount=5, description='test')
    print('Making invoice:')
    print(invoice)
    assert invoice.startswith('lnbc')
    return invoice

async def test_check_invoice(invoice: str):
    invoice_info = await nwc_relay.check_invoice(invoice=invoice)
    print('Checking invoice:')
    print(invoice_info)
    assert invoice_info['result']['invoice'] == invoice
    
async def test_pay_invoice(invoice: str):
    print('Paying invoice:')
    await nwc_relay2.try_pay_invoice(invoice)

async def test_did_payment_succeed(invoice: str):
    preimage = await nwc_relay.did_payment_succeed(invoice)
    print('Checking invoice payment success:')
    print("Paid" if preimage else "Not paid")
    return True if preimage else False

async def test_get_info():
    info = await nwc_relay.get_info()
    print('Getting info:')
    print(info)
    assert info['result']['pubkey']

async def test_list_transactions():
    transactions = await nwc_relay.list_transactions()
    print('Listing transactions:')
    assert transactions['result']['transactions']
    return len(transactions['result']['transactions'])

async def test_get_balance():
    balance = await nwc_relay.get_balance()
    print('Getting balance:')
    print(balance)
    assert balance['result']['balance']

async def test_suite():
    await test_get_info()
    await test_get_balance()
    await test_list_transactions()
    invoice = await test_make_invoice()
    await test_check_invoice(invoice)
    assert not await test_did_payment_succeed(invoice)
    await test_pay_invoice(invoice)
    await asyncio.sleep(5)
    assert await test_did_payment_succeed(invoice)


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_suite())
    