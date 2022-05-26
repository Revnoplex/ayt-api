from .async_youtube_api import AsyncYoutubeAPI
from typing import Literal, NamedTuple

__title__ = "ayt-api"
__author__ = "Revnoplex"
__license__ = "MIT"
__copyright__ = "Copyright 2022 Revnoplex"
__version__ = "0.1.0"


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    release_level: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info = VersionInfo(major=0, minor=1, micro=0, release_level="final", serial=0)
