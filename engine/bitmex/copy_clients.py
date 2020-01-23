import os
import sys
import bitmex
import json
import time
from datetime import date, datetime

clientOrders = {}
copy_clients = []
lvrgPrcnt = 1
mainBalance = 1.0


__DIR__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, __DIR__)
sys.path.insert(0, __DIR__ + '/../')

from modules.helper import *

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
def init_copy_clients( MainBalance, resetArgs, symbols):
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
		bitmex_key = key_secret[0]
		bitmex_secret = key_secret[1]
		testnet = key_secret[2]
		accName = key_secret[3]
		try:
			newClient = bitmex.bitmex(test=(testnet=='testnet'),api_key=bitmex_key, api_secret=bitmex_secret )
			if resetArgs[0]:
				upd = newClient.Order.Order_cancelAll().result()
				console_message(accName+': all orders were cancelled!', 'bitmex')
			if resetArgs[1]:
				for sym in symbols:
					upd = newClient.Order.Order_closePosition(symbol=sym).result()
					print(upd)
					console_message(accName+': position on ' + sym + ' was closed!', 'bitmex')
					
			thisBalance = newClient.User.User_getMargin().result()
			copy_clients.append( newClient )
			copy_clients[-1]._id = key_secret[0]
			
			thisBalance = thisBalance[0]['availableMargin']
			copy_clients[-1].BlncRate = thisBalance/MainBalance
			copy_clients[-1].accName = accName
			copy_clients[-1].active = True
			print('Client-to-main ratio balance: '+ str(copy_clients[-1].BlncRate))
			clientOrders[key_secret[0]] = {}
		except Exception as ex:
			console_message('Client Initialization failed: '+ str(ex), 'bitmex')
			

def update_copy_clients( MainBalance, resetArgs, symbols):
	global copy_clients
	
	prevClients_IDs = []
	for client in copy_clients:
		prevClients_IDs.append(client._id)
	f = open(__DIR__ + '/copy_clients.txt', 'r')
	creds = f.read().split('\n')
	f.close()
	for cr in creds:
		if len(cr)<2 or cr.startswith('#'):
			continue
		key_secret = cr.split('   ')
		bitmex_key = key_secret[0]
		bitmex_secret = key_secret[1]
		testnet = key_secret[2]
		accName = key_secret[3]
		if bitmex_key in prevClients_IDs:
			continue
		print(key_secret)
		try:
			newClient = bitmex.bitmex(test=(testnet=='testnet'),api_key=bitmex_key, api_secret=bitmex_secret )
			if resetArgs[0]:
				upd = newClient.Order.Order_cancelAll().result()
				console_message(accName+': all orders were cancelled!', 'bitmex')
			if resetArgs[1]:
				for sym in symbols:
					upd = newClient.Order.Order_closePosition(symbol=sym).result()
					print(upd)
					console_message(accName+': position on ' + sym + ' was closed!', 'bitmex')
					
			thisBalance = newClient.User.User_getMargin().result()
			copy_clients.append( newClient )
			copy_clients[-1]._id = bitmex_key
			
			thisBalance = thisBalance[0]['availableMargin']
			copy_clients[-1].BlncRate = thisBalance/MainBalance
			copy_clients[-1].accName = accName
			copy_clients[-1].active = True
			print('Client-to-main ratio balance: '+ str(copy_clients[-1].BlncRate))
			clientOrders[key_secret[0]] = {}
		except Exception as ex:
			console_message('Client Initialization failed: '+ str(ex), 'bitmex')



def copy_order( client, message, count):
	
	# offload JSON data from the socket message
	orderData = message['data'][0]
	try:
		if orderData['ordType']=='Market' and orderData['ordStatus']=='New':
			symb = orderData['symbol']
			ordSide = orderData['side']
			closePos = orderData['execInst']
			if closePos == 'Close':
				upd = client.Order.Order_closePosition(symbol=symb).result()
				bMessage = ''
				if count==1:
					bMessage = 'MASTER ACCOUNT: Closed a Position, for the '+ upd[0]['symbol'] + ' pair \n\n'
				clientMsg = client.accName+': Closed a Position, Quantity: ' + str(upd[0]['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair'
				console_message(clientMsg, 'bitmex')
				bMessage = bMessage + clientMsg
			else:
				ordQty = orderData['orderQty']*client.BlncRate
				upd = client.Order.Order_new(symbol=symb, orderQty=ordQty, ordType='Market', side=ordSide).result()
				#print('CLIENT-'+client.accName+': Placed New Market Order, Quantity: ' + str(upd[0]['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair')
				bMessage = ''
				if count==1:
					bMessage = 'MASTER ACCOUNT: Placed New Market Order, Quantity: ' + str( orderData['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair \n\n'
				clientMsg = client.accName+': Placed New Market Order, Quantity: ' + str(upd[0]['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair'
				console_message(clientMsg, 'bitmex')
				bMessage = bMessage + clientMsg
				
		if orderData['ordType']=='Limit' and orderData['ordStatus']=='New':
			symb = orderData['symbol']
			ordPrice = orderData['price']
			ordSide = orderData['side']
			execInst = orderData['execInst']
			tIFrc = orderData['timeInForce']
			if execInst != 'Close':
				ordQty = orderData['orderQty']*client.BlncRate
			if execInst == 'Close':
				upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, price=ordPrice, ordType='Limit', side=ordSide).result()
			else:
				upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty, price=ordPrice, ordType='Limit', side=ordSide).result()
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT: Placed a New Limit-Order, Price: ' + str(upd[0]['price']) + \
									' Quantity: ' + str(orderData['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair\n\n'						
			clientMsg = client.accName+': Placed a New Limit-Order, Price: ' + str(upd[0]['price']) + \
					' Quantity: ' + str(upd[0]['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair'
			console_message(clientMsg, 'bitmex')
			bMessage = bMessage + clientMsg

		if orderData['ordType']=='Stop' and orderData['ordStatus']=='New':
			symb = orderData['symbol']
			ordQty = orderData['orderQty']*client.BlncRate
			ordStopPx = orderData['stopPx']
			ordSide = orderData['side']
			ordType = orderData['ordType']
			execInst = orderData['execInst']
			tIFrc = orderData['timeInForce']
			if orderData['pegPriceType'] == 'TrailingStopPeg':
				pegOffset = orderData['pegOffsetValue']
				upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty, ordType=ordType, side=ordSide , pegOffsetValue=pegOffset).result()
			else:
				upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty, ordType=ordType, side=ordSide , stopPx=ordStopPx).result()
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT: Placed a New Stop-Market Order, Stopx: ' + str(upd[0]['stopPx']) + \
					' Quantity: ' + str(orderData['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair \n\n'
			clientMsg = client.accName+': Placed a New Stop-Market Order, Stopx: ' + str(upd[0]['stopPx']) + \
					' Quantity: ' + str(upd[0]['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair'
			console_message(clientMsg, 'bitmex')
			bMessage = bMessage + clientMsg
					
		if orderData['ordType']=='StopLimit' and orderData['ordStatus']=='New':
			symb = orderData['symbol']
			ordQty = orderData['orderQty']*client.BlncRate
			ordPrice = orderData['price']
			ordStopPx = orderData['stopPx']
			ordSide = orderData['side']
			execInst = orderData['execInst']
			tIFrc = orderData['timeInForce']
			upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty, price=ordPrice, ordType='StopLimit', side=ordSide , stopPx=ordStopPx).result()	
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT: Placed a New Stop-Limit Order, Price: ' + str(upd[0]['price']) + ' StopPx: ' + str(upd[0]['stopPx']) + \
					' Quantity: ' + str(orderData['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair \n\n'
			clientMsg =client.accName+': Placed a New Stop-Limit Order, Price: ' + str(upd[0]['price']) + ' StopPx: ' + str(upd[0]['stopPx']) + \
					' Quantity: ' + str(upd[0]['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair'
			console_message(clientMsg, 'bitmex')
			bMessage = bMessage + clientMsg
					
		if orderData['ordType']=='MarketIfTouched' and orderData['ordStatus']=='New':
			symb = orderData['symbol']
			ordQty = orderData['orderQty']*client.BlncRate
			ordStopPx = orderData['stopPx']
			ordSide = orderData['side']
			execInst = orderData['execInst']
			tIFrc = orderData['timeInForce']
			upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty, ordType='MarketIfTouched', side=ordSide , stopPx=ordStopPx).result()	
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT: Placed a New Take-Profit-Market Order, StopPx: ' + str(upd[0]['stopPx']) + \
					' Quantity: ' + str(orderData['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair \n\n'
			clientMsg = client.accName+': Placed a New Take-Profit-Market Order, StopPx: ' + str(upd[0]['stopPx']) + \
					' Quantity: ' + str(upd[0]['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair'
			console_message(clientMsg, 'bitmex')
			bMessage = bMessage + clientMsg
			
		if orderData['ordType']=='LimitIfTouched' and orderData['ordStatus']=='New':
			symb = orderData['symbol']
			ordQty = orderData['orderQty']*client.BlncRate
			ordPrice = orderData['price']
			ordStopPx = orderData['stopPx']
			ordSide = orderData['side']   
			execInst = orderData['execInst']
			tIFrc = orderData['timeInForce']
			upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty,  price=ordPrice, ordType='LimitIfTouched', side=ordSide , stopPx=ordStopPx).result()
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT: Placed a New Take-Profit-Limit Order, Price: ' + str(upd[0]['price']) + ' StopPx: ' + str(upd[0]['stopPx']) + \
					' Quantity: ' + str(orderData['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair \n\n'
			clientMsg = client.accName+': Placed a New Take-Profit-Limit Order, Price: ' + str(upd[0]['price']) + ' StopPx: ' + str(upd[0]['stopPx']) + \
					' Quantity: ' + str(upd[0]['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair'
			console_message(clientMsg, 'bitmex')
			bMessage = bMessage + clientMsg
			
		#print(upd[0])
		if orderData['ordType']!='Market':
			clientOrders[client._id][orderData['orderID']] = upd[0]['orderID']
		#print(clientOrders)
	except Exception as ex:
		    console_message(client.accName+' ' +str(ex), 'bitmex')


def update_order( client, message, action):
	
	# offload JSON data from the socket message
	orderData = message['data'][0]
	try:	
		if client._id in clientOrders.keys():
			pass
	except Exception as ex:
		    console_message(client.accName+' ' +str(ex), 'bitmex')
		    return

	try:
		ordId = clientOrders[client._id][orderData['orderID']]
		if action == 'price':
			ordPrice = orderData['price']
			upd = client.Order.Order_amend(orderID=ordId, price=ordPrice).result()
			console_message(client.accName+': Updating Limit-Order, new Price: ' + str(upd[0]['price']) + ' for the '+ upd[0]['symbol'] + ' pair', 'bitmex');

		elif action == 'stopPx':
			ordPx = orderData['stopPx']
			upd = client.Order.Order_amend(orderID=ordId, stopPx=ordPx).result()
			console_message(client.accName+': Updating Stop-Order, new stopPx: ' + str(upd[0]['stopPx']) + ' for the '+ upd[0]['symbol'] + ' pair', 'bitmex')

		elif action == 'pegOffsetValue':
			pegOffset = orderData['pegOffsetValue']
			upd = client.Order.Order_amend(orderID=ordId, pegOffsetValue=pegOffset).result()
			console_message(client.accName+': Updating Stop-Order, new stopPx: ' + str(upd[0]['stopPx']) + ' for the '+ upd[0]['symbol'] + ' pair', 'bitmex')
			
		else:
			ordQty = orderData['orderQty']
			upd = client.Order.Order_amend(orderID=ordId, orderQty=ordQty*client.BlncRate).result()
			console_message(client.accName+': Updating Limit-Order, new Quantity: ' + str(upd[0]['orderQty']) + ' for the '+ upd[0]['symbol'] + ' pair', 'bitmex')
		
	except Exception as ex:
		    console_message(client.accName+' ' +str(ex), 'bitmex')


def update_position( client, message, action):
	posData = message['data'][0]
	if 'crossMargin' in message['data'][0].keys():
		if message['data'][0]['crossMargin']==True:
			posData['leverage'] = 0.0
		if message['data'][0]['crossMargin']==False and 'leverage' not in message['data'][0].keys():
			try:	
				upd = client.Position.Position_isolateMargin(symbol=posData['symbol']).result()
				console_message(client.accName+': Isolated Margin for '+ upd[0]['symbol'] + ' position', 'bitmex')
				return
			except Exception as ex:
				console_message(client.accName+' ' +str(ex), 'bitmex')
				
	try:	
		upd = client.Position.Position_updateLeverage(symbol=posData['symbol'], leverage=lvrgPrcnt*posData['leverage']).result()
		console_message(client.accName+': Updating Leverage for '+ upd[0]['symbol'] + ' position', 'bitmex')
	except Exception as ex:
		console_message(client.accName+' ' +str(ex), 'bitmex')

def cancel_order( client, message):

	for orderData in message['data']:
		# offload JSON data from the socket message
		# orderData = message['data'][0]
		try:	
			if client._id in clientOrders.keys():
				console_message(client.accName+": Cancelling OrderID: " + clientOrders[client._id][orderData['orderID']], 'bitmex')
		except Exception as ex:
				console_message(client.accName+' ' +str(ex), 'bitmex')
		try:
			ordId = clientOrders[client._id][orderData['orderID']]
			upd = client.Order.Order_cancel(orderID=ordId).result()
			#print(upd)
		except Exception as ex:
				console_message(client.accName+' ' +str(ex), 'bitmex')
