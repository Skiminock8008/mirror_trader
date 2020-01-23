
from binance.client import Client
from binance.enums import *
from datetime import date, datetime
import json
import time
import ccxt # for the OCO orders
from modules.helper import *

# global variables (seen by the main_account.py too)
clientOrders = {}
ocoOrders = { }
copy_clients = []
lvrgPrcnt = 1
mainBalance = 1.0


# ------ HELPER FUNCTIONS --------------
def get_clients():
    return copy_clients
    
'''
	This function initializes the 'copy-clients' according to their
	balance-ratio to the main-account. That's the only argument for this function
'''
def init_copy_clients( MainBalance ):
	global copy_clients
     
	f = open('copy_clients.txt', 'r')
	creds = f.read().split('\n')
	f.close()
	#registerTelegramCommands()
	for cr in creds:
		if len(cr)<2 or cr.startswith('#'):
			continue
		key_secret = cr.split('   ')
		print("Client Initiliazed: " +str(key_secret) )
		binance_api_key = key_secret[0]
		binance_api_secret = key_secret[1]
		accName = key_secret[2]
		try:
			newClient = Client(binance_api_key, binance_api_secret)
			newClient.ccxtClient = ccxt.binance({ 'apiKey': binance_api_key, 'secret': binance_api_secret,'enableRateLimit': True})
					
			thisBalance = float(newClient.get_asset_balance(asset='BTC')['free'])
			copy_clients.append( newClient )
			copy_clients[-1]._id = key_secret[0]
			
			thisBalance = 1.0 # thisBalance['free']
			copy_clients[-1].BlncRate = float(thisBalance)/MainBalance
			copy_clients[-1].accName = accName
			copy_clients[-1].active = True
			print('Client-to-main ratio balance: '+ str(copy_clients[-1].BlncRate))
			clientOrders[key_secret[0]] = {}
			ocoOrders[key_secret[0]] = {}
		except Exception as ex:
			print('Client Initialization failed: '+ str(ex) )
     


def copy_order( client, message, count):
	
	# offload JSON data from the socket message
	orderData = message
	notUpd = True
	try:
		if (orderData['o']=='TAKE_PROFIT_LIMIT' or orderData['o']=='STOP_LOSS_LIMIT') and orderData['X']=='NEW' and orderData['g']!=-1:
			ocoOrders[client._id][orderData['g']] = orderData
			notUpd = False

		if orderData['o']=='LIMIT_MAKER' and orderData['X']=='NEW' and orderData['g']!=-1:
			symb = orderData['s']
			ordSide = orderData['S']
			tIFrc = orderData['f']
			ordPrice = orderData['p']
			ordQty = float(orderData['q'])*client.BlncRate
			stopOrder = ocoOrders[client._id][orderData['g']]
			stopPrice = stopOrder['P']
			stopLimitPrice = stopOrder['p']
			upd = client.ccxtClient.private_post_order_oco({ "symbol": symb, "side": ordSide, "quantity": ordQty, "price": ordPrice, "stopPrice": stopPrice, 
							"stopLimitPrice": stopLimitPrice, "stopLimitTimeInForce": tIFrc})
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT:: Placed a New OCO-Order, with orderListId: ' + str(upd['orderListId']) + \
									' Quantity: ' + str(ordQty) +' for the '+ upd['symbol'] + ' pair\n\n'			
			clientMsg = client.accName+':: Placed a New OCO-Order: Quantity: ' + str(ordQty) + ' for the '+ upd['symbol'] + ' pair'
			console_message(clientMsg, "binance")
			upd["orderId"] = upd["orders"][0]["orderId"]
			bMessage = bMessage + clientMsg
			

		if orderData['o']=='MARKET' and orderData['X']=='NEW':
			symb = orderData['s']
			ordSide = orderData['S']
			tIFrc = orderData['f']
			ordQty = float(orderData['q'])*client.BlncRate
			#upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty, price=ordPrice, ordType='Limit', side=ordSide).result()
			upd = client.create_order( symbol=symb , side=ordSide, type=ORDER_TYPE_MARKET, quantity=ordQty)
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT:: Placed a New MARKET-Order, Price: ' + str(orderData['p']) + \
									' Quantity: ' + str(orderData['q']) + ' for the '+ orderData['s'] + ' pair\n\n'			
			clientMsg = client.accName+':: Placed a New MARKET-Order'  + \
							' Quantity: ' + str(upd['origQty']) + ' for the '+ upd['symbol'] + ' pair'
			console_message(clientMsg, "binance")
			bMessage = bMessage + clientMsg

		if orderData['o']=='LIMIT' and orderData['X']=='NEW':
			symb = orderData['s']
			ordPrice = orderData['p']
			ordSide = orderData['S']
			tIFrc = orderData['f']
			ordQty = float(orderData['q'])*client.BlncRate

			#upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty, price=ordPrice, ordType='Limit', side=ordSide).result()
			upd = client.create_order( symbol=symb , side=ordSide, type=ORDER_TYPE_LIMIT, timeInForce=tIFrc, quantity=ordQty, price=ordPrice)
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT:: Placed a New LIMIT-Order, Price: ' + str(orderData['p']) + \
									' Quantity: ' + str(orderData['q']) + ' for the '+ orderData['s'] + ' pair\n\n'			
			clientMsg = client.accName+':: Placed a New Limit-Order, Price: ' + str(upd['price']) + \
					' Quantity: ' + str(upd['origQty']) + ' for the '+ upd['symbol'] + ' pair'
			console_message(clientMsg, "binance")
			bMessage = bMessage + clientMsg

		if (orderData['o']=='TAKE_PROFIT_LIMIT' or orderData['o']=='STOP_LOSS_LIMIT') and orderData['X']=='NEW' and orderData['g']==-1:
			symb = orderData['s']
			ordPrice = orderData['p']
			stopPrice = orderData['P']
			ordSide = orderData['S']
			tIFrc = orderData['f']
			ordQty = float(orderData['q'])*client.BlncRate

			#upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty, price=ordPrice, ordType='Limit', side=ordSide).result()
			upd = client.create_order( symbol=symb, side=ordSide, type=orderData['o'], timeInForce=tIFrc, quantity=ordQty, price=ordPrice, stopPrice=stopPrice)
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT:: Placed a New STOP-LIMIT-Order, Price: ' + str(orderData['p']) + 'stopPrice: ' + str(orderData['P']) + \
									' Quantity: ' + str(orderData['q']) + ' for the '+ orderData['s'] + ' pair\n\n'
			clientMsg = client.accName+':: Placed a New Limit-Order, Price: ' + str(ordPrice) + \
						' Quantity: ' + str(ordQty) + ' for the '+ upd['symbol'] + ' pair'
			console_message(clientMsg, "binance")
			bMessage = bMessage + clientMsg

		if (orderData['o']=='TAKE_PROFIT' or orderData['o']=='STOP_LOSS') and orderData['X']=='NEW':
			symb = orderData['s']
			ordPrice = orderData['p']
			stopPrice = orderData['P']
			ordSide = orderData['S']
			tIFrc = orderData['f']
			ordQty = float(orderData['q'])*client.BlncRate

			#upd = client.Order.Order_new(symbol=symb, execInst=execInst, timeInForce=tIFrc, orderQty=ordQty, price=ordPrice, ordType='Limit', side=ordSide).result()
			upd = client.create_order( symbol=symb, side=ordSide, type=orderData['o'], quantity=ordQty, stopPrice=stopPrice)
			bMessage = ''
			if count==1:
				bMessage = 'MASTER ACCOUNT:: Placed a New Stop-Order, stopPrice: ' + str(orderData['P']) + \
									' Quantity: ' + str(orderData['q']) + ' for the '+ orderData['s'] + ' pair\n\n'
			clientMsg = client.accName+':: Placed a New Limit-Order, Price: ' + str(ordPrice) + \
						' Quantity: ' + str(ordQty) + ' for the '+ upd['symbol'] + ' pair'
			console_message(clientMsg, "binance")
			bMessage = bMessage + clientMsg

		#print(upd)
		if orderData['o']!='MARKET' and notUpd:
			clientOrders[client._id][orderData['i']] = upd['orderId']
		#print(clientOrders)
	except Exception as ex:
			console_message(client.accName+' ' +str(ex), "binance")



def cancel_order( client, message):

	orderData = message
	# offload JSON data from the socket message
	# orderData = message['data'][0]
	try:	
		if client._id in clientOrders.keys():
			console_message(client.accName+":: Cancelling OrderID: " + str(clientOrders[client._id][orderData['i']]), "binance")
	except Exception as ex:
			console_message(client.accName+' ' +str(ex), "binance")
	try:
		ordId = clientOrders[client._id][orderData['i']]
		client.cancel_order( symbol=orderData['s'], orderId=ordId)
		#print(upd)
	except Exception as ex:
			console_message(client.accName+' ' +str(ex), "binance")
