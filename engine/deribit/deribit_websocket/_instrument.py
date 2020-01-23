import alog

from deribit_websocket._deribit_websocket import DeribitWebsocket

# from bitmex_websocket.constants import Channels, SecureChannels, \
#     SecureInstrumentChannels

__all__ = ['Instrument']


class SubscribeToAtLeastOneChannelException(Exception):
    pass


class SubscribeToSecureChannelException(Exception):
    pass


class Instrument(DeribitWebsocket):
    def __init__(self,
                 symbol: str='XBTUSD',
                 channels: [Channels] or [str]=None,
                 should_auth=False, **kwargs):

        super().__init__(should_auth=should_auth, **kwargs)

        if channels is None:
            raise SubscribeToAtLeastOneChannelException()

        self.channels = channels

        if should_auth is False and self._channels_contains_secure():
            raise SubscribeToSecureChannelException()

        self.symbol = symbol
        self.on('action', self.on_action)

    def run_forever(self, **kwargs):
        self.on('subscribe', self.subscribe_channels)
        super().run_forever(**kwargs)

    def subscribe_channels(self):
        for channel in self.channels:
            channel_key = f'{channel.name}:{self.symbol}'
            self.subscribe(channel_key)

    def on_action(self, message):
        alog.debug(alog.pformat(message))

    # def _channels_contains_secure(self):
    #     secure_channels = list(SecureChannels) + list(SecureInstrumentChannels)
    #     return not set(secure_channels).isdisjoint(self.channels)
