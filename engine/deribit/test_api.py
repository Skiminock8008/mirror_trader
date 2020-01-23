from deribitapi import Deribit

client = Deribit('FXFPjr4f', 'gWcSsCN4XH2M1Q9JDFUT16SfiyQwhHmmJED1BuuCAAI')

msg = \
{
  "jsonrpc" : "2.0",
  "id" : 2515,
  "method" : "private/get_account_summary",
  "params" : {
    "currency" : "BTC",
    "extended" : True
  }
}
params = {"instrument_name": "BTC-PERPETUAL", "amount": 1000, "type": "limit", "price": 8700.0, "max_show": 1000, "post_only": "false", "reduce_only": "false"}
#response = client._curl_bitmex("/private/sell", params, max_retries=0)
response = client._curl_bitmex("/public/get_instruments", {"currency": "BTC"}, max_retries=0)
for inst in response['result']:
    print('user.orders.' + inst['instrument_name'] + '.raw\n')
#print(str(response)) 