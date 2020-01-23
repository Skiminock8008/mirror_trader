from requests.auth import AuthBase
import time
import base64
from datetime import datetime

from auth.APIKeyAuth import generate_signature


class APIKeyAuthWithExpires(AuthBase):

    """Attaches API Key Authentication to the given Request object. This implementation uses `expires`."""

    def __init__(self, apiKey, apiSecret):
        """Init with Key & Secret."""
        self.apiKey = apiKey
        self.apiSecret = apiSecret

    def __call__(self, r):
        """
        Called when forming a request - generates api key headers. This call uses `expires` instead of nonce.

        This way it will not collide with other processes using the same API Key if requests arrive out of order.
        For more details, see https://docs.deribit.com/v2/?python#authentication
        """
        # modify and return the request
        expires = int(round(time.time()) + 5)  # 5s grace period in case of clock skew   
        timestamp = round(datetime.now().timestamp() * 1000)     
        signature = generate_signature(self.apiSecret, r.method, r.url, expires, r.body or '', timestamp)
        # Authorization: deri-hmac-sha256 id=ClientId,ts=Timestamp,sig=Signature,nonce=Nonce
        r.headers['Authorization'] = 'deri-hmac-sha256 id={},ts={},sig={},nonce={}'.format(self.apiKey, timestamp, signature, expires)
        return r
