from .api import AsyncYoutubeAPI, version_info
from .exceptions import *

__title__ = "ayt-api"
__author__ = "Revnoplex"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2022-2023 Revnoplex"
__version__ = ".".join(map(str, version_info[:3])) + \
              ("" if version_info[3] == "final" else f"{version_info[3][0] if version_info[3] != 'candidate' else 'rc'}"
                                                     f"{version_info[4]}")
