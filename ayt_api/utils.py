import pathlib
import warnings
from typing import Optional, Any
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
    elif components.hostname.endswith("ytimg.com"):
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

    .. deprecated:: 0.4.0
        Use :func:`censor_key` instead

    Args:
        call_url (str): The api call url containing the uncensored api key.

    Returns:
        str: The url with the api key censored.
    """
    warnings.warn(
        "censor_token is deprecated since 0.4.0 and is scheduled "
        "for removal in a later release. Use censor_key instead.",
        DeprecationWarning
    )
    return censor_key(call_url)


def basic_html_page(title: str, description: str) -> str:
    """
    Builds a basic html page

    .. versionadded:: 0.4.0

    This is used in :func:`ayt_api.api.AsyncYoutubeAPI.with_oauth_flow_generator`

    Args:
        title (str): The title and heading for the page
        description (str): The description that will be displayed on the page
    Returns:
        str: The html page
    """
    return f"""\
        <!doctype html>
        <html lang="en">
        <head>
            <title>{title}</title>
            <link rel="icon" href="https://ayt-api.revnoplex.xyz/ayt-api-square.svg">
            <link rel="stylesheet" type="text/css" href="https://revnoplex.xyz/css/main.css">
        </head>
        <body>
            <h1>{title}</h1>
            <p>{description}.</p>
        </body>
        </html>\
    """


def use_existing(existing_value: Any, argument: Any) -> Any:
    """
    A check used in the updated functions to decide when to use the existing value if the argument has a value of
    ``EXISTING`` or use the value of the argument.

    .. versionadded:: 0.4.0

    Args:
        existing_value (Any): The existing value that will be used if ``argument`` is ``EXISTING``.
        argument (Any): The value to overwrite ``existing_value`` if not ``EXISTING``.

    Returns:
        Any: The existing value or argument.
    """
    from ayt_api.types import EXISTING
    return existing_value if argument is EXISTING else argument


def ensure_missing_keys(original: dict, minimised: dict) -> dict:
    """
    Ensure a dictionary with possible missing keys from the first dictionary includes them if the value for the key
    was ``None`` or an empty value.

    .. versionadded:: 0.4.0

    Note:
        This util will only check the first layer of keys and will not check any deeper nested keys.

    Args:
        original (dict): The original dictionary with the full set of keys.
        minimised (dict): The version of the dictionary that had keys with empty values removed.

    Returns:
        dict: The ``minimised`` version of the dictionary with values added back from the original depending on if they
            were empty values.
    """
    updated = minimised.copy()
    for key, value in original.items():
        if key not in minimised and (not value):
            updated[key] = value
    return updated
