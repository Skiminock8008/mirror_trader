import os
import sys
from binance.client import Client
from binance.websockets import BinanceSocketManager

__DIR__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, __DIR__)
sys.path.insert(0, __DIR__ + '/../')

from modules.helper import *

list_clients(get_clients(), 'binance')

# Read the main_account's API keys
f = open(__DIR__ + '/main_account.txt', 'r')
CREDENTIALS = f.read().split('\n')
CREDENTIALS = CREDENTIALS[0].split('   ')

print(CREDENTIALS[0])
print(CREDENTIALS[1])

binance_api_key = CREDENTIALS[0]
binance_api_secret = CREDENTIALS[1]

os.environ['BINANCE_API_KEY'] = binance_api_key
os.environ['BINANCE_API_SECRET'] = binance_api_secret


from copy_clients import copy_order
from copy_clients import init_copy_clients
from copy_clients import cancel_order
from copy_clients import get_clients

import json
client = Client(binance_api_key, binance_api_secret)

balance = client.get_asset_balance(asset='BTC')
print('Account BTC balance: '+ str(balance))
balance = client.get_asset_balance(asset='BNB')
print('Account BNB balance: '+ str(balance)+"\n")
balance = 1.0


init_copy_clients(balance)
mainOrders = []

def process_message(msg):
	# for debuggin -- printing any message's full data
	# print(msg)
	global copy_clients
	if msg['e']!='executionReport':
		return

	try:
		print('processing new message... Action: '+msg['S']+' -- Symbol: '+msg['s'])
		f = open('orders.json', 'a')
		f.write(json.dumps(msg, indent=4, sort_keys=True))
		f.close()
	except Exception as ex:
		print(ex)
	
	copy_clients = get_clients()	
	try:
		count = 0
		# main for-loop where the copy-clients are getting new trades/updates
		for cclient in copy_clients:
			if cclient.active == False:
				continue
			try:
				count = count + 1
					
				if msg['e'] == 'executionReport' and msg['x']!="CANCELED":
					if count==1:
						print('\nMASTER ACCOUNT:: Placed an order: '+str(msg) +'\n')
						if msg['o']!='MARKET':
							mainOrders.append(msg['i'])
					copy_order(cclient, msg, count)
					continue
				else:
					if 'CANCELED' == msg['x']:
						if count==1:
							print('\nMASTER ACCOUNT:: Cancelled order '+str(msg['i']))
							if msg['i'] in mainOrders:
								mainOrders.pop(mainOrders.index(msg['i']))
						cancel_order(cclient, msg)
					
			except Exception as ex:
				console_message(ex, "binance")
	except Exception as ex:
		console_message(ex, "binance")		
			 

bmWss = BinanceSocketManager(client)

bmWss.start_user_socket(process_message)

bmWss.start()
