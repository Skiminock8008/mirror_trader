import asyncio
import os
import sys

__DIR__ = os.path.dirname(os.path.realpath(__file__))
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt.async_support as ccxt  # noqa: E402


async def test():
    bitmex = ccxt.bitmex({
        'apiKey': "9NTAdyDunRjHCuCEOEiK5rMI",
        'secret': "gXtFv11oGkvQ4XtpE-xXM-oigVClwEZ2XMHKKlmpGt0kHXRq",
        'verbose': True,  # switch it to False if you don't want the HTTP log
    })
    markets = await bitmex.load_markets()
    open(__DIR__ + '/symbols.txt', 'w').close()
    
    for symbol in bitmex.symbols:
        add_to_symbols(symbol)

    await bitmex.close()

def add_to_symbols(symbol):
    with open(__DIR__ + '/symbols.txt', 'a') as file:
        if "." not in symbol:
            file.write(symbol + '\n')
        #XBTUSD not included

loop = asyncio.get_event_loop()
loop.run_until_complete(test())