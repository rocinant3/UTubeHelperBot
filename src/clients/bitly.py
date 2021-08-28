import typing
import requests

import bitly_api


class BitlyClient:
    def __init__(self, token: str):
        self.conn = bitly_api.Connection(access_token=token)

    def shorten(self, url: str) -> typing.Optional[str]:
        try:
            return self.conn.shorten(uri=url)['url']
        except bitly_api.BitlyError as e:
            print(e)
            return None
