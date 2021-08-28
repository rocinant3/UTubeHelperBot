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

    def get_short_links_on_video_time_codes(self, url: str) -> typing.List[ShortedLink]:
        video_id = parse_video_id_from_url(url)
        if not video_id:
            raise youtube_exceptions.InvalidURLError

        video_meta = self.client.get_video_meta(video_id)

        if len(video_meta['items']) == 0:
            raise youtube_exceptions.VideoDoesntExistError

        result = []
        description = video_meta['items'][0]['snippet']['description']
        time_codes = parse_description_time_codes(description)

        if len(time_codes) == 0:
            raise youtube_exceptions.TimeCodesDoesntExistError
        for time_code in time_codes:
            time_in_seconds = time_code_to_seconds(time_code=time_code.time)
            link = f'https://www.youtube.com/watch?v={video_id}&t={time_in_seconds}s'
            shorted_url = self.bitly_client.shorten(link)
            print("SHORTED")
            print(shorted_url)
            if shorted_url:
                obj = ShortedLink(description=time_code.description, shorted_link=shorted_url)
                result.append(obj)
        return result

    @staticmethod
    def shorted_links_to_html(links: typing.List[ShortedLink]) -> str:
        html = ""
        for shorted_link in links:
            html += f"{shorted_link.description} - {shorted_link.shorted_link} \n"
        return html
