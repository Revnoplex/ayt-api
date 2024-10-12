import pathlib
from typing import Optional
from urllib import parse


def extract_video_id(url: str) -> Optional[str]:
    """
    This should work for every url listed here:
    https://gist.github.com/rodrigoborgesdeoliveira/987683cfbfcc8d800192da1e73adc486#file-activeyoutubeurlformats-txt
    and more such as i.ytimg.com urls.

    Args:
        url (str): The url to strip the id from.

    Returns:
        Optional[str]: The video id with the rest of the url removed.
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
    This should work for every url listed here:
    https://github.com/Revnoplex/ayt-api/blob/main/test-playlist-urls.txt
    Don't expect this to work on YouTube mixes.

    Args:
        url (str): The url to strip the id from.

    Returns:
        Optional[str]: The playlist id with the rest of the url remove.
    """
    components = parse.urlparse(url.replace("&", "?", 1) if "?" not in url else url)
    queries = parse.parse_qs(components.query)
    encoded_query_matches = {'u', 'url'}.intersection(set(queries.keys()))
    if 'list' in queries:
        return queries["list"][0]
    elif encoded_query_matches:
        return extract_playlist_id(parse.unquote(queries[encoded_query_matches.pop()][0]))


def extract_channel_id(url: str) -> Optional[str]:
    """
    This should work for every url listed here:
    https://github.com/Revnoplex/ayt-api/blob/main/test-channel-urls.txt

    Args:
        url (str): The url to strip the id from.

    Returns:
        Optional[str]: The channel id with the rest of the url removed.
    """
    components = parse.urlparse(url.replace("&", "?", 1) if "?" not in url else url)
    queries = parse.parse_qs(components.query)
    encoded_query_matches = {'u', 'url'}.intersection(set(queries.keys()))
    if encoded_query_matches:
        return extract_channel_id(parse.unquote(queries[encoded_query_matches.pop()][0]))
    else:
        return pathlib.Path(components.path).name


def extract_comment_id(url: str) -> Optional[str]:
    """
    This should work for every url listed here:
    https://github.com/Revnoplex/ayt-api/blob/main/test-comment-urls.txt

    Args:
        url (str): The url to strip the id from.

    Returns:
        Optional[str]: The comment id with the rest of the url removed.
    """
    components = parse.urlparse(url.replace("&", "?", 1) if "?" not in url else url)
    queries = parse.parse_qs(components.query)
    encoded_query_matches = {'u', 'url'}.intersection(set(queries.keys()))
    if 'lc' in queries:
        return queries["lc"][0]
    elif encoded_query_matches:
        return extract_comment_id(parse.unquote(queries[encoded_query_matches.pop()][0]))


def id_str_to_int(youtube_id: str) -> int:
    """Converts a base 64 YouTube ID string into an integer.

    Args:
        youtube_id (str): The YouTube ID as a base 64 string.

    Returns:
        int: The YouTube ID as an integer.

    Raises:
        ValueError: There were invalid characters in the YouTube ID.
    """
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
            raise ValueError(f"Invalid YouTube ID character: {char}")
    return number


def camel_to_snake(string: str) -> str:
    """Converts words in the camel case convention to the snake case convention.

    e.g. Converts ``fooBar`` to ``foo_bar``.

    Args:
        string (str): The words in the camel case convention.

    Returns:
        str: The words in the snake case convention.
    """
    snake_string = ""
    for char in string:
        if char.isupper():
            snake_string += "_" + char.lower()
        else:
            snake_string += char
    return snake_string


def snake_to_camel(string: str) -> str:
    """Converts words in the snake case convention to the camel case convention.

    e.g. Converts ``foo_bar`` to ``fooBar``.

    Args:
        string (str): The words in the snake case convention.

    Returns:
        str: The words in the camel case convention.
    """
    camel_string = ""
    capitalise = False
    for char in string:
        if char == "_":
            capitalise = True
        elif capitalise:
            camel_string += char.upper()
            capitalise = False
        else:
            camel_string += char
    return camel_string[0].lower() + camel_string[1:]


def snake_keys(dictionary: dict) -> dict:
    """Converts keys in a dictionary from camel case to snake case.

    Args:
        dictionary (dict): The dictionary with keys using the camel case convention.

    Returns:
        dict: The dictionary with keys using the snake case convention.
    """
    snake_dict = {}
    for key, value in dictionary.items():
        snake_dict[camel_to_snake(key)] = value
    return snake_dict


def censor_key(call_url: str) -> str:
    """Censors the api key in an api call url.

    Args:
        call_url (str): The api call url containing the uncensored api key.

    Returns:
        str: The url with the api key censored.
    """
    components = parse.urlparse(call_url)
    queries = parse.parse_qs(components.query)
    if "key" in queries:
        queries["key"] = ["API_KEY"]
    censored_components = components._replace(query=parse.urlencode(queries, doseq=True))
    return censored_components.geturl()


def censor_token(call_url: str) -> str:
    """Alias of censor_key

    Args:
        call_url (str): The api call url containing the uncensored api key.

    Returns:
        str: The url with the api key censored.
    """
    return censor_key(call_url)
