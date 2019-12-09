import os
import sys

__DIR__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, __DIR__)
sys.path.insert(0, __DIR__ + '/../')

from modules.helper import *


list_clients(get_clients(), 'bitmex')

# Read the main_account's API keys - also do check if is testnet or not
f = open(__DIR__ + '/main_account.txt', 'r')
CREDENTIALS = f.read().split('\n')
CREDENTIALS = CREDENTIALS[0].split('   ')

bitmex_key = CREDENTIALS[0]
bitmex_secret = CREDENTIALS[1]
testnet = CREDENTIALS[2]

os.environ['BITMEX_API_KEY'] = bitmex_key
os.environ['BITMEX_API_SECRET'] = bitmex_secret
if testnet == 'testnet':
	os.environ["RUN_ENV"] = 'development'
else:
	os.environ["RUN_ENV"] = 'live'

import bitmex
from bitmex_websocket import Instrument
from copy_clients import copy_order
from copy_clients import init_copy_clients
from copy_clients import update_copy_clients
from copy_clients import update_order
from copy_clients import cancel_order
from copy_clients import update_position
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
	mainClient = bitmex.bitmex(api_key=bitmex_key, 
				   api_secret=bitmex_secret)
else:
	mainClient = bitmex.bitmex( test=False, api_key=bitmex_key, 
				   api_secret=bitmex_secret)

balance = mainClient.User.User_getMargin().result()
balance = balance[0]['availableMargin']
print('Account XBT balance: '+ str(balance))

websocket.enableTrace(True)

f = open(__DIR__ + '/symbols.txt', 'r')
symbols = f.read().split('\n')
f.close()
#symbols = ['XBTUSD', 'ADAxxx', 'LTCxxx' ...]

#copy_clients = init_copy_clients(balance)
init_copy_clients(balance, resetArgs , symbols)
mainOrders = []

def process_message(msg):
	# for debuggin -- printing any message's full data
	# print(msg)
	global copy_clients
	
	if msg['table'] == 'position':
		if 'leverage' not in msg['data'][0].keys():
			if 'crossMargin' not in msg['data'][0].keys():
				return
	try:
		print('processing new message... Action:'+msg['action']+' -- Symbol:'+msg['data'][0]['symbol'])
		if msg['action'] != 'partial':
			if msg['action'] == 'update' and (msg['data'][0]['orderID'] not in mainOrders):
				return
			f = open(__DIR__ + '/orders.json', 'a')
			f.write(json.dumps(msg, indent=4, sort_keys=True))
			f.close()
	except Exception as ex:
		print(ex)
	
	update_copy_clients( balance, resetArgs , symbols)
	copy_clients = get_clients()	
	try:
		count = 0
		for cclient in copy_clients:
			if cclient.active == False:
				continue
			try:
				count = count + 1
				if msg['table'] == 'position' and ('leverage' in msg['data'][0].keys() or 'crossMargin' in msg['data'][0].keys()):
					if  msg['data'][0]['liquidationPrice'] != 0:
						update_position(cclient, msg, 'price')
						continue
					
				if msg['action'] =='insert':
					if count==1:
						print ('\nMASTER ACCOUNT:: Placed an order: '+str(msg['data'][0]) +'\n')
						if msg['data'][0]['ordType']!='Market':
							mainOrders.append(msg['data'][0]['orderID'])
					copy_order(cclient, msg, count)
					continue
					
				if msg['action'] == 'update':
					msgKeys = msg['data'][0].keys()
					
					if 'price' in msgKeys:
						if count==1:
							print ('\nMASTER ACCOUNT:: Updated Price: '+str(msg['data'][0]) +'\n')
						update_order(cclient, msg, 'price')
						continue

					if 'pegOffsetValue' in msgKeys:
						if count==1:
							print ('\nMASTER ACCOUNT:: Updated stopPx: '+str(msg['data'][0]) +'\n')
						update_order(cclient, msg, 'pegOffsetValue')
						continue
						
					if 'stopPx' in msgKeys:
						if count==1:
							print ('\nMASTER ACCOUNT:: Updated stopPx: '+str(msg['data'][0]) +'\n')
						update_order(cclient, msg, 'stopPx')
						
					if 'orderQty' in msgKeys:
						if count==1:
							print ('\nMASTER ACCOUNT:: Updated Quantity: '+str(msg['data'][0]) +'\n')
						update_order(cclient, msg, 'orderQty')
						
					if 'ordStatus' in msgKeys:
						if 'Canceled' == msg['data'][0]['ordStatus']:
							if count==1:
								for cnclOrd in msg['data']:
									print('\nMASTER ACCOUNT:: Cancelled order '+cnclOrd['orderID'])
									if cnclOrd['orderID'] in mainOrders:
										mainOrders.pop(mainOrders.index(cnclOrd['orderID']))
							cancel_order(cclient, msg)
			except Exception as ex:
				print(ex)
	except Exception as ex:
		print(ex)		
			 
for sym in symbols:
	new_sock = Instrument(symbol=sym,
                      # subscribes to 'order' channel (order submission, update, cancellation etc.)
                      channels=['order', 'position'],
                      # environment must be set according to pdf
                      shouldAuth=True)

	# subscribe to action events for this instrument
	# new_sock.on('action', lambda x: print("# action message: %s" % x))
	new_sock.on('action', lambda x: process_message(x))


loop = asyncio.get_event_loop()
loop.run_forever()
