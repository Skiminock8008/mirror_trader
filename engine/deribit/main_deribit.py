import os
import sys

__DIR__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, __DIR__)
sys.path.insert(0, __DIR__ + '/../')

from modules.helper import *


list_clients(get_clients(), 'deribit')

# Read the deribit API keys - also do check if is testnet or not
f = open(__DIR__ + '/main_account.txt', 'r')
CREDENTIALS = f.read().split('\n')
CREDENTIALS = CREDENTIALS[0].split('   ')

api_key = CREDENTIALS[0]
api_secret = CREDENTIALS[1]
testnet = CREDENTIALS[2]

os.environ['DERIBIT_API_KEY'] = api_key
os.environ['DERIBIT_API_SECRET'] = api_secret
if testnet == 'testnet':
	os.environ["RUN_ENV"] = 'development'
else:
	os.environ["RUN_ENV"] = 'live'

from deribitapi import Deribit
from deribit_websocket import DeribitWebsocket
from copy_clients import copy_order
from copy_clients import init_copy_clients
# from copy_clients import update_copy_clients
from copy_clients import update_order
from copy_clients import cancel_order
# from copy_clients import update_position
from copy_clients import get_clients

import asyncio
import websocket
import json

# reset copy-clients options
resetArgs = [False, False]
try:
	args = sys.argv
	if 'resetpos' in args:
		resetArgs[1] = True
	elif 'resetord' in args:
		resetArgs[0] = True
except:
	pass
	
if testnet == 'testnet':
	mainClient = Deribit(apiKey=api_key, 
				   apiSecret=api_secret)
else:
	mainClient = Deribit( test=False, apiKey=api_key, 
				   apiSecret=api_secret)

btc_balance, eth_balance = mainClient.get_balance()
balance = btc_balance
print('Account XBT balance: '+ str(balance))

# websocket.enableTrace(True)

f = open(__DIR__ + '/symbols.txt', 'r')
symbols = f.read().split('\n')
f.close()
#symbols = ['XBTUSD', 'ADAxxx', 'LTCxxx' ...]

#copy_clients = init_copy_clients(balance)
init_copy_clients(btc_balance, eth_balance, resetArgs , symbols)
mainOrders = []

def process_message(channel, data):
	# for debuggin -- printing any message's full data
	print(channel + ' : ' + str(data))
	global copy_clients

	try:
		print('processing new message... state:'+data['order_state']+' -- Symbol:'+data['symbol'])
		
		if data['replaced'] and (data['order_id'] not in mainOrders):
			return
		f = open(__DIR__ + '/orders.json', 'a')
		f.write(json.dumps(data, indent=4, sort_keys=True))
		f.close()
	except Exception as ex:
		print(ex)
	
	# update_copy_clients( balance, resetArgs , symbols)
	# copy_clients = get_clients()	
	try:
		order_id = data['order_id']
		order_type = data['order_type']
		order_state = data['order_state']
		replaced = data['replaced']

		insert = False
		cancelled = False
		if not replaced:
			if order_type == 'limit' and order_state == 'open':
    				insert = True
			elif order_type == 'market' and (order_state == 'open' or order_state == 'filled'):
    				insert = True
			elif order_state == 'untriggered':
    				insert = True
		
		if order_id not in mainOrders:
    			insert = True
		if order_state == 'cancelled':
    			cancelled = True


		if cancelled:
			print('\nMASTER ACCOUNT:: Cancelled order '+order_id)
		elif replaced:
			print ('\nMASTER ACCOUNT:: Updated Price: '+str(data) +'\n')
		elif insert:
			mainOrders.append(order_id)
			print ('\nMASTER ACCOUNT:: Placed an order: '+str(data) +'\n')

		try:
			if cancelled:
				cancel_order(data)
			elif replaced:
				update_order(data)
			elif insert:
				copy_order(data)
		except Exception as ex:
			print(ex)
	except Exception as ex:
		print(ex)
			 
channels = []
if 'btc_usd' in symbols:
		try :
			response = mainClient.get_instruments()
			for inst in response['result']:
				channels.append('user.orders.' + inst['instrument_name'] + '.raw')
		except Exception as ex:
			print(ex)
			channels.append('user.orders.BTC-PERPETUAL.raw')

if 'eth_usd' in symbols:
		try :
			response = mainClient.get_instruments("ETH")
			for inst in response['result']:
				channels.append('user.orders.' + inst['instrument_name'] + '.raw')
		except Exception as ex:
			print(ex)
			channels.append('user.orders.ETH-PERPETUAL.raw')

new_sock = DeribitWebsocket(api_key, 
				api_secret,
				channels=channels,
				should_auth=True)
				
new_sock.on('orders', lambda channel, data: process_message(channel, data))
new_sock.run_forever()

# loop = asyncio.get_event_loop()
# loop.run_forever()
