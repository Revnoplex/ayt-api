import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Union

from .types import YoutubeVideo, YoutubeChannel, YoutubePlaylist


class ChannelType(Enum):
    show = "show"
    any = "any"

    def __str__(self):
        return self.value


class EventType(Enum):
    completed = "completed"
    live = "live"
    upcoming = "upcoming"

    def __str__(self):
        return self.value


class Order(Enum):
    date = "date"
    rating = "rating"
    relevance = "relevance"
    title = "title"
    video_count = "view_count"
    view_count = "view_count"

    def __str__(self):
        return self.value


class SafeSearch(Enum):
    moderate = "moderate"
    none = "none"
    strict = "strict"

    def __str__(self):
        return self.value


class VideoCaption(Enum):
    closed_caption = "closed_caption"
    none = "none"
    any = "any"

    def __str__(self):
        return self.value


class VideoDimension(Enum):
    _2d = "2d"
    _3d = "3d"
    any = "any"

    def __str__(self):
        return self.value


class VideoDuration(Enum):
    long = "long"
    medium = "medium"
    short = "short"
    any = "any"

    def __str__(self):
        return self.value


class VideoEmbeddable(Enum):
    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoPaidProductPlacement(Enum):
    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoSyndicated(Enum):
    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoType(Enum):
    episode = "episode"
    movie = "movie"
    any = "any"

    def __str__(self):
        return self.value


class VideoLicense(Enum):
    creative_common = "creative_common"
    youtube = "youtube"
    any = "any"

    def __str__(self):
        return self.value


class VideoDefinition(Enum):
    high = "high"
    standard = "standard"
    any = "any"

    def __str__(self):
        return self.value


@dataclass
class SearchFilter:
    channel_id: str = None
    published_after: Union[str, int, datetime.datetime] = None
    published_before: Union[str, int, datetime.datetime] = None
    region_code: str = None
    relevance_language: str = None
    topic_id: str = None
    video_category_id: str = None
    channel_type: Union[ChannelType, str] = None
    event_type: Union[str, EventType] = None
    order: Union[str, Order] = None
    safe_search: Union[str, SafeSearch] = None
    _type: Union[str, type[Union[YoutubeVideo, YoutubeChannel, YoutubePlaylist]]] = None
    video_caption: Union[str, VideoCaption] = None
    video_definition: Union[str, VideoDefinition] = None
    video_dimension: Union[str, VideoDimension] = None
    video_duration: Union[str, VideoDuration] = None
    video_embeddable: Union[str, VideoEmbeddable] = None
    video_license: Union[str, VideoLicense] = None
    video_paid_product_placement: Union[str, VideoPaidProductPlacement] = None
    video_syndicated: Union[str, VideoSyndicated] = None
    video_type: Union[str, VideoType] = None
