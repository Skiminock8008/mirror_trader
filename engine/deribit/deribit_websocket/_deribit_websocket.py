# from bitmex_websocket.auth.api_key_auth import generate_nonce,\
#     generate_signature
#from deribit_websocket.settings import settings
from pyee import EventEmitter
from urllib.parse import urlparse
from websocket import WebSocketApp

import alog
import json
import ssl
import time
import threading
from time import time, sleep

__all__ = ['DeribitWebsocket']


class DeribitWebsocketConnectionError(Exception):
    pass


class DeribitWebsocket(
    WebSocketApp,
    EventEmitter
):
    def __init__(
        self,
        api_key,
        api_secret,
        channels=None,
        test=True,
        should_auth=False,
        heartbeat=True,
        ping_interval=10,
        ping_timeout=9,
        **kwargs
    ):
        self.ping_timeout = ping_timeout
        self.ping_interval = ping_interval
        self.should_auth = should_auth
        self.heartbeat = heartbeat
        self.channels = channels
        self.reconnect_count = 0

        self.api_key = api_key
        self.api_secret = api_secret

        super().__init__(
            url=self.gen_url(test),
            header=self.header(),
            on_message=self.on_message,
            on_close=self.on_close,
            on_open=self.on_open,
            on_error=self.on_error,
            on_pong=self.on_pong,
            **kwargs
        )
        super(EventEmitter, self).__init__()

        self._id = -1
        self._method = None

        self._authInfo = {}
        
        self._init_emit()

    def gen_url(self, test):
        if test:
            base_url = 'https://test.deribit.com/ws/api/v2'
        else:
            base_url = 'https://www.deribit.com/api/v2'
        url_parts = list(urlparse(base_url))


        # query_string = ''

        # if self.heartbeat:
        #     query_string = '?heartbeat=true'

        # url = "wss://{}/realtime{}".format(url_parts[1], query_string)
        url = "wss://{}/ws/api/v2".format(url_parts[1])

        alog.info(url)
        return url

    def run_forever(self, **kwargs):
        """Connect to the websocket in a thread."""

        # setup websocket.run_forever arguments
        ws_run_args = {
            'sslopt': {"cert_reqs": ssl.CERT_NONE}
        }

        if self.heartbeat:
            ws_run_args['ping_timeout'] = self.ping_timeout
            ws_run_args['ping_interval'] = self.ping_interval

        alog.debug(ws_run_args)

        super().run_forever()

    def on_pong(self, message):
        timestamp = float(time.time() * 1000)
        latency = timestamp - (self.last_ping_tm * 1000)
        self.emit('latency', latency)

    def subscribe(self, channel: [str]):
        subscription_msg = {}
        if self.should_auth:
            method = "private/subscribe"
            subscription_msg["access_token"] = self._authInfo["access_token"]
        else:
            method = "public/subscribe", 
        subscription_msg["channels"] = channel
        self._send_message(method, subscription_msg)

    def _send_message(self, method, params):
        self._method = method
        self._id += 1
        
        message = \
        {
            "jsonrpc" : "2.0",
            "id" : self._id,
            "method" : self._method,
            "params" : params
        }
        msg = json.dumps(message)
        alog.info("sending request: " + str(msg))
        self.send(msg)

    def is_connected(self):
        return self.sock.connected

    @staticmethod
    def on_subscribe(message):
        alog.debug("Subscribed to %s." % message)
        # if message['success']:
        #     alog.debug("Subscribed to %s." % message['subscribe'])
        # else:
        #     raise Exception('Unable to subsribe.')

    def on_message(self, message):
        """Handler for parsing WS messages."""
        response = json.loads(message)
        
        # if response
        if "id" in response:
            if "result" in response:
                result = response["result"]
            elif "error" in response:
                alog.error(response["error"])
                return
            else:
                return
            
            id = response["id"]
            if id == self._id:
                if self._method == "public/auth":
                    self._authInfo["access_token"] = result["access_token"]
                    self._authInfo["expires_in"] = result["expires_in"]
                    self._authInfo["refresh_token"] = result["refresh_token"]
                    self._authInfo["scope"] = result["scope"]
                    self._authInfo["token_type"] = result["token_type"]
                    
                    alog.info("access_token: {}".format(self._authInfo["access_token"]))
                    
                    self.emit('subscribe')

                    # wst = threading.Thread(target=self.__on_expires_in)
                    # wst.daemon = True
                    # wst.start()
                    return
                elif self._method == "public/subscribe" or self._method == "private/subscribe":
                    self.emit('subscribed', result)
                    return

                
        alog.info(message)
        if "method" in response:
            method = response["method"]
            if method == "subscription":
                params = response["params"]
                channel = params["channel"]
                #if "user.orders" in channel:
                self.emit('orders', channel, params["data"])

    def header(self):
        """Return auth headers. Will use API Keys if present in settings."""
        auth_header = []

        # if self.should_auth:
        #     alog.info("Authenticating with API Key.")
        #     # To auth to the WS using an API key, we generate a signature
        #     # of a nonce and the WS API endpoint.
        #     alog.debug(settings.BITMEX_API_KEY)
        #     nonce = generate_nonce()
        #     api_signature = generate_signature(
        #         settings.BITMEX_API_SECRET, 'GET', '/realtime', nonce, '')

        #     auth_header = [
        #         "api-nonce: " + str(nonce),
        #         "api-signature: " + api_signature,
        #         "api-key:" + settings.BITMEX_API_KEY
        #     ]

        return auth_header

    def on_open(self):
        alog.debug("Websocket Opened.")
            
        if self.should_auth:
            self.emit('auth')

        self.emit('open')

    def on_close(self):
        alog.info('Websocket Closed')

    def on_error(self, error):
        alog.error(error)
        raise DeribitWebsocketConnectionError(error)
        
    def _init_emit(self):        
        self.on('subscribed', self.on_subscribe)
        self.on('auth', self._auth)
        self.on('subscribe', self.subscribe_channels)

    def subscribe_channels(self):
        self.subscribe(self.channels)
        
    # def __on_expires_in(self):
    #     expires = int(self._authInfo["expires_in"])
    #     alog.info(str(self._authInfo))
    #     start = time()
    #     while (time() - start < expires):
    #         sleep(10)
    #     alog.info("expired")
    #     self._auth(True)

    def _auth(self, refresh=False):
        if refresh:
            params = {
                "grant_type" : "refresh_token",
                "refresh_token" : self._authInfo["refresh_token"],
                "scope" : self._authInfo["scope"]
            }
        else:
            params = {
                "grant_type" : "client_credentials",
                "client_id" : self.api_key,
                "client_secret" : self.api_secret
            }
        
        self._send_message("public/auth", params)

