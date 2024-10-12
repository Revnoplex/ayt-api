from .api import AsyncYoutubeAPI
from typing import NamedTuple as _NamedTuple
from .exceptions import *
from .filters import SearchFilter
from . import utils
from . import filters
from .enums import *

__title__ = "ayt-api"
__author__ = "Revnoplex"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2022-2023 Revnoplex"
__version__ = "0.3.0"


class VersionInfo(_NamedTuple):
    major: int
    minor: int
    micro: int
    release_level: str
    serial: int


_matches = [("alpha", "a"), ("beta", "b"), ("candidate", "rc"), ("final", "")]

_suffix = __version__.split(".")[-1][1:]

_serial = ""
_release_letter = ""

for _char in _suffix:
    if _char.isdecimal():
        _serial += _char
    else:
        _release_letter += _char

_release_level = "".join([match[0] for match in _matches if _release_letter in match])

version_info = VersionInfo(major=int(__version__.split(".")[0]), minor=int(__version__.split(".")[1]),
                           micro=int(__version__.split(".")[2][0]), release_level=_release_level or "final",
                           serial=int(_serial or 0))
