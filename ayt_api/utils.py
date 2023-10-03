import pathlib
from typing import Optional
from urllib import parse


def extract_video_id(url: str) -> Optional[str]:
    """
    This should work for every url listed here:
    https://gist.github.com/rodrigoborgesdeoliveira/987683cfbfcc8d800192da1e73adc486#file-activeyoutubeurlformats-txt
    and more.
    Args:
        url (str): The url to strip the id from
    Returns:
        Optional[str]: The video id with the rest of the url removed
    """
    components = parse.urlparse(url.replace("&", "?", 1) if "?" not in url else url)
    queries = parse.parse_qs(components.query)
    encoded_query_matches = {'u', 'url'}.intersection(set(queries.keys()))
    if 'v' in queries:
        return queries["v"][0]
    elif encoded_query_matches:
        return extract_video_id(parse.unquote(queries[encoded_query_matches.pop()][0]))
    elif components.netloc == "i.ytimg.com":
        return pathlib.Path(components.path).parts[2]
    elif pathlib.Path(components.path).name not in ["playlist"]:
        return pathlib.Path(components.path).name


def extract_playlist_id(url: str) -> Optional[str]:
    """
    This should work with the following urls

    Don't expect this to work on YouTube mixes
    Args:
        url (str): The url to strip the id from
    Returns:
        Optional[str]: The playlist id with the rest of the url removed
    """
    components = parse.urlparse(url.replace("&", "?", 1) if "?" not in url else url)
    queries = parse.parse_qs(components.query)
    encoded_query_matches = {'u', 'url'}.intersection(set(queries.keys()))
    if 'list' in queries:
        return queries["list"][0]
    elif encoded_query_matches:
        return extract_playlist_id(parse.unquote(queries[encoded_query_matches.pop()][0]))


def id_as_base_10(youtube_id: str):
    number = 0
    last_chars = ["-", "_"]
    for idx, char in enumerate(reversed(youtube_id)):
        ord_var = ord(char)
        if 65 <= ord_var <= 90:
            number += (ord_var - 65) * 64 ** idx
        elif 97 <= ord_var <= 122:
            number += (ord_var - 71) * 64 ** idx
        elif 48 <= ord_var <= 57:
            number += (ord_var + 4) * 64 ** idx
        elif char in last_chars:
            number += (62 + last_chars.index(char)) * 64 ** idx
        else:
            raise ValueError
    return number
