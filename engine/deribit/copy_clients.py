import os
import sys
import json
import time
from datetime import date, datetime

from deribitapi import Deribit
from modules.helper import *

clientOrders = {}
copy_clients = []
lvrgPrcnt = 1
mainBalance = 1.0


__DIR__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, __DIR__)
sys.path.insert(0, __DIR__ + '/../')


# ------ HELPER FUNCTIONS --------------
def get_clients():
    return copy_clients
    
def toggle_client(num, changeState):
	global copy_clients
	try:
		if num=="all":
			for cc in copy_clients:
				cc.active = changeState
			return True
		copy_clients[int(num)].active = changeState
		return True
	except Exception as ex:
		return False

'''
	This function initializes the 'copy-clients' according to their
	balance-ratio to the main-account. That's the only argument for this function
'''
def init_copy_clients( mainBtcBalance, mainEthBalance, resetArgs, symbols):
	global copy_clients
     
	f = open(__DIR__ + '/copy_clients.txt', 'r')
	creds = f.read().split('\n')
	f.close()
	#registerTelegramCommands()
	for cr in creds:
		if len(cr)<2 or cr.startswith('#'):
			continue
		key_secret = cr.split('   ')
		print(key_secret)
		api_key = key_secret[0]
		api_secret = key_secret[1]
		testnet = key_secret[2]
		accName = key_secret[3]
		try:
			newClient = Deribit(test=(testnet=='testnet'),apiKey=api_key, apiSecret=api_secret )

			if resetArgs[0]:
				upd = newClient.cancel_all()
				console_message(accName+': all orders were cancelled!', "deribit")
				print(upd)
			if resetArgs[1]:
				if 'btc_usd' in symbols:
					upd = newClient.close_position('BTC-PERPETUAL')
					print(upd)
					console_message(accName+': btc position on ' + sym + ' was closed!', "deribit")
				if 'eth_usd' in symbols:
					upd = newClient.close_position('ETH-PERPETUAL')
					print(upd)
					console_message(accName+': eth position on ' + sym + ' was closed!', "deribit")
					
			btcBal, ethBal = newClient.get_balance()
			copy_clients.append( newClient )
			copy_clients[-1]._id = key_secret[0]
			
			if mainBtcBalance > 0:
				copy_clients[-1].btcBlncRate = btcBal/mainBtcBalance
			if mainEthBalance > 0:
				copy_clients[-1].ethBlncRate = ethBal/mainEthBalance
			copy_clients[-1].accName = accName
			copy_clients[-1].active = True
			print('Client-to-main ratio balance: '+ str(copy_clients[-1].btcBlncRate))
			clientOrders[key_secret[0]] = {}
		except Exception as ex:
			console_message('Client Initialization failed: '+ str(ex), "deribit")
			

# def update_copy_clients( MainBalance, resetArgs, symbols):
# 	global copy_clients
	
# 	prevClients_IDs = []
# 	for client in copy_clients:
# 		prevClients_IDs.append(client._id)
# 	f = open(__DIR__ + '/copy_clients.txt', 'r')
# 	creds = f.read().split('\n')
# 	f.close()
# 	for cr in creds:
# 		if len(cr)<2 or cr.startswith('#'):
# 			continue
# 		key_secret = cr.split('   ')
# 		bitmex_key = key_secret[0]
# 		bitmex_secret = key_secret[1]
# 		testnet = key_secret[2]
# 		accName = key_secret[3]
# 		if bitmex_key in prevClients_IDs:
# 			continue
# 		print(key_secret)
# 		try:
# 			newClient = bitmex.bitmex(test=(testnet=='testnet'),api_key=bitmex_key, api_secret=bitmex_secret )
# 			if resetArgs[0]:
# 				upd = newClient.Order.Order_cancelAll().result()
# 				console_message(accName+': all orders were cancelled!', "deribit")
# 			if resetArgs[1]:
# 				for sym in symbols:
# 					upd = newClient.Order.Order_closePosition(symbol=sym).result()
# 					print(upd)
# 					console_message(accName+': position on ' + sym + ' was closed!', "deribit")
					
# 			thisBalance = newClient.User.User_getMargin().result()
# 			copy_clients.append( newClient )
# 			copy_clients[-1]._id = bitmex_key
			
# 			thisBalance = thisBalance[0]['availableMargin']
# 			copy_clients[-1].BlncRate = thisBalance/MainBalance
# 			copy_clients[-1].accName = accName
# 			copy_clients[-1].active = True
# 			print('Client-to-main ratio balance: '+ str(copy_clients[-1].BlncRate))
# 			clientOrders[key_secret[0]] = {}
# 		except Exception as ex:
# 			console_message('Client Initialization failed: '+ str(ex) , "deribit")



def copy_order(message):
	count = 0
	global copy_clients
	for client in copy_clients:
		if client.active == False:
			continue
		count += 1
		# offload JSON data from the socket message
		orderData = message
		try:
			msg={}
			msg['instrument_name'] = orderData['instrument_name']
			amount = orderData['amount'] * client.btcBlncRate if 'BTC' in orderData['instrument_name'] else client.ethBlncRate
			msg['amount'] = int(amount) // 10 * 10
			msg['type'] = orderData['order_type']
			msg['price'] = orderData['price']
			msg['max_show'] = orderData['max_show']
			msg['post_only'] = "true" if orderData['post_only'] else "false"
			msg['reduce_only'] = "true" if orderData['reduce_only'] else "false"
			if 'stop_price' in orderData:
				msg['stop_price'] = orderData['stop_price']
			if 'trigger' in orderData:
				msg['trigger'] = orderData['trigger']
			# if 'advanced' in orderData and orderData['orderData'] =="usd":
			# 	msg['trigger'] = orderData['trigger']

			if orderData['direction'] == "sell":
				upd = client.sell(msg)
			elif orderData['direction'] == "buy":
				upd = client.buy(msg)
				
			
			# bMessage = ''
			# if count==1:
			# 	bMessage = 'MASTER ACCOUNT: Placed a New Limit-Order, Price: ' + str(upd[0]['price']) + \
			# 						' Quantity: ' + str(orderData['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair\n\n'						
			clientMsg = client.accName+': Placed a New Order: ' + str(upd)
			console_message(clientMsg, "deribit")
			# bMessage = bMessage + clientMsg
				
			#print(upd[0])
			# if orderData['ordType']!='Market':
			# 	clientOrders[client._id][orderData['orderID']] = upd[0]['orderID']
			#print(clientOrders)
			
			clientOrders[client._id][orderData['order_id']] = upd['result']['order']['order_id']
		except Exception as ex:
			console_message(client.accName+' ' +str(ex), "deribit")


def update_order(message):
	count = 0
	global copy_clients
	for client in copy_clients:
		if client.active == False:
			continue
		count += 1
		# offload JSON data from the socket message
		orderData = message
	
		try:
			ordId = clientOrders[client._id][orderData['order_id']]
			msg={}
			msg['order_id'] = ordId
			amount = orderData['amount'] * client.btcBlncRate if 'BTC' in orderData['instrument_name'] else client.ethBlncRate
			msg['amount'] = int(amount) // 10 * 10
			msg['price'] = orderData['price']
			msg['post_only'] = "true" if orderData['post_only'] else "false"
			if 'stop_price' in orderData:
				msg['stop_price'] = orderData['stop_price']

			upd = client.edit(msg)
			console_message(client.accName+': Updating Order : ' + str(upd), "deribit")
			
		except Exception as ex:
				console_message(client.accName+' ' +str(ex), "deribit")


# def update_position( client, message, action):
# 	posData = message['data'][0]
# 	if 'crossMargin' in message['data'][0].keys():
# 		if message['data'][0]['crossMargin']==True:
# 			posData['leverage'] = 0.0
# 		if message['data'][0]['crossMargin']==False and 'leverage' not in message['data'][0].keys():
# 			try:	
# 				upd = client.Position.Position_isolateMargin(symbol=posData['symbol']).result()
# 				console_message(client.accName+': Isolated Margin for '+ upd[0]['symbol'] + ' position', "deribit")
# 				return
# 			except Exception as ex:
# 				console_message(client.accName+' ' +str(ex), "deribit")
				
# 	try:	
# 		upd = client.Position.Position_updateLeverage(symbol=posData['symbol'], leverage=lvrgPrcnt*posData['leverage']).result()
# 		console_message(client.accName+': Updating Leverage for '+ upd[0]['symbol'] + ' position', "deribit")
# 	except Exception as ex:
# 		console_message(client.accName+' ' +str(ex), "deribit")

def cancel_order(message):
	orderData = message
	global copy_clients
	for client in copy_clients:    		
			if client.active == False:
					continue
			
			try:	
				if client._id in clientOrders.keys():
					console_message(client.accName+": Cancelling OrderID: " + clientOrders[client._id][orderData['orderID']], "deribit")
			except Exception as ex:
					console_message(client.accName+' ' +str(ex), "deribit")
			try:
				ordId = clientOrders[client._id][orderData['order_id']]
				upd = client.cancel(ordId)
				print(upd)
			except Exception as ex:
					console_message(client.accName+' ' +str(ex), "deribit")
