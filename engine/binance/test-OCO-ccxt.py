
# Read the main_account's API keys
binance_api_key = 'YOUR_KEY'
binance_api_secret = 'YOUR_SECRET'
import ccxt  # noqa: E402

exchange = ccxt.binance({
    'apiKey': binance_api_key,
    'secret': binance_api_secret,
    'enableRateLimit': False,
})


symbol = 'XLMETH'
type = 'market'  # or 'market'
side = 'sell'  # or 'buy'
amount = "66.0"
price = "0.00054"  # or None
stopPrice = "0.00027"

# extra params and overrides if needed
params = {
    #'test': True,  # test if it's valid, but don't actually place it
}


#order = exchange.private_post_order_oco(symbol, type, side, amount, price, params)
order = exchange.private_post_order_oco({ "symbol": symbol, "side": side, "quantity": amount, "price": price, "stopPrice": stopPrice,
                                        "stopLimitPrice": stopPrice, "stopLimitTimeInForce": "GTC"})

print(order)

'''
    {'orderListId': 1546121, 'contingencyType': 'OCO', 'listStatusType': 'EXEC_STARTED', 
    'listOrderStatus': 'EXECUTING', 'listClientOrderId': 'JZXBSffJ2Crqk3SE5e4auH', 
    'transactionTime': 1579195442071, 'symbol': 'XLMETH', 
    'orders': [
    {'symbol': 'XLMETH', 'orderId': 88679063, 'clientOrderId': 'Sva71M2OfAKiCPKHasSOn7'}, 
    {'symbol': 'XLMETH', 'orderId': 88679064, 'clientOrderId': 'CSMIgaTpWBu1Z2GR0Gi35w'}], 
    'orderReports': [{'symbol': 'XLMETH', 'orderId': 88679063, 'orderListId': 1546121, 
    'clientOrderId': 'Sva71M2OfAKiCPKHasSOn7', 'transactTime': 1579195442071, 
    'price': '0.00027000', 'origQty': '66.00000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 
    'timeInForce': 'GTC', 'type': 'STOP_LOSS_LIMIT', 'side': 'SELL', 'stopPrice': '0.00027000'}, 
    {'symbol': 'XLMETH', 'orderId': 88679064, 'orderListId': 1546121, 'clientOrderId': 'CSMIgaTpWBu1Z2GR0Gi35w', 
    'transactTime': 1579195442071, 'price': '0.00054000', 'origQty': '66.00000000', 
    'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT_MAKER', 'side': 'SELL'}]}
'''


