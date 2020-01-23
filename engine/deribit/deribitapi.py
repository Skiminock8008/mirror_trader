import requests
import json
import logging

from auth import APIKeyAuthWithExpires

class Deribit(object):
    def __init__(self, apiKey, apiSecret, test=True, timeout=7):
        if test:
            self.host = 'https://test.deribit.com/api/v2'
        else:
            self.host = 'https://www.deribit.com/api/v2'

        self.api_key = apiKey
        self.api_secret = apiSecret
        
        # Prepare HTTPS session
        self.session = requests.Session()
        # These headers are always sent
        # self.session.headers.update({'user-agent': 'liquidbot-' + constants.VERSION})
        self.session.headers.update({'content-type': 'application/json'})
        self.session.headers.update({'accept': 'application/json'})

        self.timeout = timeout
        self.retries = 0

        self.logger = logging.getLogger('root')
    def get_instruments(self, currency="BTC"):
        return self._curl_bitmex("/public/get_instruments", {"currency": currency}, max_retries=0)
        
    #
    # Authentication required methods
    #
    def authentication_required(fn):
        """Annotation for methods that require auth."""
        def wrapped(self, *args, **kwargs):
            if not (self.api_key):
                msg = "You must be authenticated to use this method"
                raise Exception(msg)
            else:
                return fn(self, *args, **kwargs)
        return wrapped

    @authentication_required
    def get_balance(self):
        
        params = {
            "currency" : "BTC"
        }
        response = self._curl_bitmex("/private/get_account_summary", params, max_retries=0)
        btc_balance = response['result']['margin_balance']
        params = {
            "currency" : "ETH"
        }
        response = self._curl_bitmex("/private/get_account_summary", params, max_retries=0)
        eth_balance = response['result']['margin_balance']

        return btc_balance, eth_balance
    
    @authentication_required
    def cancel_all(self):
        return self._curl_bitmex("/private/cancel_all", {}, max_retries=0)

    @authentication_required
    def buy(self, param):
        return self._curl_bitmex("/private/buy", param, max_retries=0)

    @authentication_required
    def sell(self, param):
        return self._curl_bitmex("/private/sell", param, max_retries=0)

    @authentication_required
    def cancel(self, ordID):
        param = {'order_id': ordID}
        return self._curl_bitmex("/private/cancel", param, max_retries=0)

    @authentication_required
    def edit(self, param):
        return self._curl_bitmex("/private/edit", param, max_retries=0)
        
    @authentication_required
    def close_position(self, instrument ,market=True, price=None):
        type = 'market' if market else 'limit'
        params = {
            "type" : type,
            "instrument_name" : instrument
        }
        if not market:
            params['price'] = price

        return self._curl_bitmex("/private/close_position", params, max_retries=0)

    def _curl_bitmex(self, path, query=None, postdict=None, timeout=None, verb=None, rethrow_errors=False,
                     max_retries=None):
        """Send a request to BitMEX Servers."""
        # Handle URL
        url = self.host + path

        if timeout is None:
            timeout = self.timeout

        # Default to POST if data is attached, GET otherwise
        if not verb:
            verb = 'POST' if postdict else 'GET'

        # By default don't retry POST or PUT. Retrying GET/DELETE is okay because they are idempotent.
        # In the future we could allow retrying PUT, so long as 'leavesQty' is not used (not idempotent),
        # or you could change the clOrdID (set {"clOrdID": "new", "origClOrdID": "old"}) so that an amend
        # can't erroneously be applied twice.
        if max_retries is None:
            max_retries = 0 if verb in ['POST', 'PUT'] else 3

        def exit_or_throw(e):
            self.retries = 0

            if rethrow_errors:
                raise e
            else:
                exit(1)

        # def retry():
        #     self.retries += 1
        #     if self.retries > max_retries:
        #         raise Exception("Max retries on %s (%s) hit, raising." % (path, json.dumps(postdict or '')))
        #     return self._curl_bitmex(path, query, postdict, timeout, verb, rethrow_errors, max_retries)

        while self.retries <= max_retries:
            if self.retries > 0:
                self.logger.info("retry request")
                
            # Auth: API Key/Secret
            auth = APIKeyAuthWithExpires(self.api_key, self.api_secret)

            # Make the request
            response = None

            try:
                # self.logger.info("sending req to %s: %s" % (url, json.dumps(postdict or query or '')))
                print("sending req to %s: %s" % (url, json.dumps(postdict or query or '')))
                req = requests.Request(verb, url, json=postdict, auth=auth, params=query)
                prepped = self.session.prepare_request(req)
                response = self.session.send(prepped, timeout=timeout)
                # Make non-200s throw
                response.raise_for_status()

            except requests.exceptions.HTTPError as e:
                if response is None:
                    self.logger.error("Response is null, %s" % e)
                    self.retries += 1
                    continue

                # 401 - Auth error. This is fatal.
                if response.status_code == 401:
                    self.logger.error("API Key or Secret incorrect, please check and restart.")
                    self.logger.error("Error: " + response.text)
                    if postdict:
                        self.logger.error(postdict)
                    # Always exit, even if rethrow_errors, because this is fatal
                    # exit(1)
                    exit_or_throw(e)

                # 404, can be thrown if order canceled or does not exist.
                elif response.status_code == 404:
                    if verb == 'DELETE':
                        self.logger.error("Order not found: %s" % postdict['orderID'])
                        return
                    self.logger.error("Unable to contact the BitMEX API (404). " +
                                    "Request: %s \n %s" % (url, json.dumps(postdict)))
                    exit_or_throw(e)

                # 429, ratelimit; cancel orders & wait until X-RateLimit-Reset
                elif response.status_code == 429:
                    self.logger.error("Ratelimited on current request. Sleeping, then trying again. Try fewer " +
                                    "order pairs or contact support@bitmex.com to raise your limits. " +
                                    "Request: %s \n %s" % (url, json.dumps(postdict)))

                    # Figure out how long we need to wait.
                    ratelimit_reset = response.headers['X-RateLimit-Reset']
                    to_sleep = int(ratelimit_reset) - int(time.time())
                    reset_str = datetime.datetime.fromtimestamp(int(ratelimit_reset)).strftime('%X')

                    # We're ratelimited, and we may be waiting for a long time. Cancel orders.
                    self.logger.warning("Canceling all known orders in the meantime.")
                    self.cancel([o['orderID'] for o in self.open_orders()])

                    self.logger.error("Your ratelimit will reset at %s. Sleeping for %d seconds." % (reset_str, to_sleep))
                    time.sleep(to_sleep)

                    # Retry the request.
                    self.retries += 1
                    continue

                # 503 - BitMEX temporary downtime, likely due to a deploy. Try again
                elif response.status_code == 503:
                    self.logger.warning("Unable to contact the BitMEX API (503), retrying. " +
                                        "Request: %s \n %s" % (url, json.dumps(postdict)))
                    # sleep 5 sec
                    time.sleep(3)
                    time.sleep(2)
                    # set max_retries to 12
                    max_retries = 12.

                    # Retry the request.
                    self.retries += 1
                    continue

                elif response.status_code == 400:
                    error = response.json()['error']
                    message = error['message'].lower() if error else ''

                    # Duplicate clOrdID: that's fine, probably a deploy, go get the order(s) and return it
                    if 'duplicate clordid' in message:
                        orders = postdict['orders'] if 'orders' in postdict else postdict

                        IDs = json.dumps({'clOrdID': [order['clOrdID'] for order in orders]})
                        orderResults = self._curl_bitmex('/order', query={'filter': IDs}, verb='GET')

                        for i, order in enumerate(orderResults):
                            if (
                                    order['orderQty'] != abs(postdict['orderQty']) or
                                    order['side'] != ('Buy' if postdict['orderQty'] > 0 else 'Sell') or
                                    order['price'] != postdict['price'] or
                                    order['symbol'] != postdict['symbol']):
                                self.retries = 0
                                raise Exception('Attempted to recover from duplicate clOrdID, but order returned from API ' +
                                                'did not match POST.\nPOST data: %s\nReturned order: %s' % (
                                                    json.dumps(orders[i]), json.dumps(order)))
                        # All good
                        return orderResults

                    elif 'insufficient available balance' in message:
                        self.logger.error('Account out of funds. The message: %s' % error['message'])
                        exit_or_throw(Exception('Insufficient Funds'))


                # If we haven't returned or re-raised yet, we get here.
                self.logger.error("Unhandled Error: %s: %s" % (e, response.text))
                self.logger.error("Endpoint was: %s %s: %s" % (verb, path, json.dumps(postdict)))

                # exit_or_throw(e)

                self.retries += 1
                continue
            except requests.exceptions.Timeout as e:
                # Timeout, re-run this request
                self.logger.warning("Timed out on request: %s (%s), retrying..." % (path, json.dumps(postdict or '')))
                # return retry()
                self.retries += 1
                continue

            except requests.exceptions.ConnectionError as e:
                self.logger.warning("Unable to contact the BitMEX API (%s). Please check the URL. Retrying. " +
                                    "Request: %s %s \n %s" % (e, url, json.dumps(postdict)))
                time.sleep(1)
                # return retry()
                self.retries += 1
                continue

            # Reset retry counter on success
            self.retries = 0

            return response.json()

        self.retries = 0
        raise Exception("Max retries on %s (%s) hit, raising." % (path, json.dumps(postdict or '')))