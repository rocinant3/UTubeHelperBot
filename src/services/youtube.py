import typing
from collections import namedtuple

from clients.youtube import YoutTubeClient
from clients.bitly import BitlyClient
from exceptions import youtube as youtube_exceptions


from utils.youtube import parse_description_time_codes, time_code_to_seconds, parse_video_id_from_url


ShortedLink = namedtuple("ShortedLink", ("description", "shorted_link"))


class YoutubeService:
    def __init__(self, dev_key: str, bitly_key: str):
        self.bitly_client = BitlyClient(token=bitly_key)
        self.client = YoutTubeClient(token=dev_key)

    def _extract_time_codes(self, description: str, video_id: str, short_urls: bool = False) -> typing.List[ShortedLink]:
        result = []
        time_codes = parse_description_time_codes(description)

        if len(time_codes) == 0:
            raise youtube_exceptions.TimeCodesDoesntExistError
        for time_code in time_codes:
            time_in_seconds = time_code_to_seconds(time_code=time_code.time)
            link = f'https://youtu.be/watch?v={video_id}&t={time_in_seconds}s'
            if short_urls:
                shorted_url = self.bitly_client.shorten(link)
            else:
                shorted_url = link
            if shorted_url:
                obj = ShortedLink(description=time_code.description, shorted_link=shorted_url)
                result.append(obj)
        return result

    @staticmethod
    def parse_video_id(url: str) -> str:
        video_id = parse_video_id_from_url(url)
        if not video_id:
            raise youtube_exceptions.InvalidURLError
        return video_id

    def extract_time_codes(self, url: str, short_urls: bool = False) -> typing.List[ShortedLink]:
        video_id = self.parse_video_id(url)
        video_meta = self.client.get_video_meta(video_id)
        if len(video_meta['items']) == 0:
            raise youtube_exceptions.VideoDoesntExistError
        description = video_meta['items'][0]['snippet']['description']

        return self._extract_time_codes(description, video_id, short_urls)

    @staticmethod
    def time_codes_to_html(links: typing.List[ShortedLink], replace_http: bool = True) -> str:
        html = ""
        for shorted_link in links:
            link = shorted_link.shorted_link
            if replace_http:
                link = link.replace("https://", "")
            html += f"{shorted_link.description} » {link}\n"
        return html
