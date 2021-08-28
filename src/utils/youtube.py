import re
import typing
from urllib.parse import urlparse
from collections import namedtuple


minutes_pattern = re.compile(r'(?<!\d:)(?<!\d)[0-9]?\d:[0-9]\d(?!:?\d)')
hours_pattern = re.compile(r"(?:[0-9]\d|[0-9]*):(?:[0-9]\d):(?:[0-9]\d)")


def find_time_code(string: str) -> typing.Optional[str]:
    try:
        return hours_pattern.search(string).group(0)
    except AttributeError:
        pass
    try:
        return minutes_pattern.search(string).group(0)
    except AttributeError:
        pass
    return None


TimeCode = namedtuple("TimeCode", ("time", "description"))


def parse_description_time_codes(description) -> typing.List[TimeCode]:
    result = []
    for sentence in description.split('\n'):
        time_code = find_time_code(sentence)
        if not time_code:
            continue
        _description = sentence.replace(time_code, "").replace('-', '').strip()
        result.append(TimeCode(time=time_code, description=_description))
    return result


def time_code_to_seconds(time_code: str) -> int:
    parts = time_code.split(':')
    minutes = 0
    hours = 0
    seconds = 0
    if len(parts) == 2:
        minutes = int(parts[0])
        seconds = int(parts[1])
    elif len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])

    total_seconds = seconds
    if hours != 0:
        total_seconds += hours*60*60
    if minutes != 0:
        total_seconds += minutes*60
    return total_seconds


d = "https://www.youtube.com/watch?v=R60AJS8_o5M&t=3136s&ab_channel=MoneyWork"


def parse_video_id_from_url(url: str) -> typing.Optional[str]:
    pattern = re.compile(
        r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})')
    result = pattern.search(url)
    if result:
        return result.group(1)
    return None


def is_valid_url(url: str) -> bool:
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if regex.search(url):
        return True
    return False
