import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Union

from .types import YoutubeVideo, YoutubeChannel, YoutubePlaylist


class ChannelTypeFilter(Enum):
    show = "show"
    any = "any"

    def __str__(self):
        return self.value


class EventTypeFilter(Enum):
    completed = "completed"
    live = "live"
    upcoming = "upcoming"

    def __str__(self):
        return self.value


class OrderFilter(Enum):
    date = "date"
    rating = "rating"
    relevance = "relevance"
    title = "title"
    video_count = "view_count"
    view_count = "view_count"

    def __str__(self):
        return self.value


class SafeSearchFilter(Enum):
    moderate = "moderate"
    none = "none"
    strict = "strict"

    def __str__(self):
        return self.value


class VideoCaptionFilter(Enum):
    closed_caption = "closed_caption"
    none = "none"
    any = "any"

    def __str__(self):
        return self.value


class VideoDimensionFilter(Enum):
    _2d = "2d"
    _3d = "3d"
    any = "any"

    def __str__(self):
        return self.value


class VideoDurationFilter(Enum):
    long = "long"
    medium = "medium"
    short = "short"
    any = "any"

    def __str__(self):
        return self.value


class VideoEmbeddableFilter(Enum):
    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoPaidProductPlacementFilter(Enum):
    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoSyndicatedFilter(Enum):
    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoTypeFilter(Enum):
    episode = "episode"
    movie = "movie"
    any = "any"

    def __str__(self):
        return self.value


class VideoLicenseFilter(Enum):
    creative_common = "creative_common"
    youtube = "youtube"
    any = "any"

    def __str__(self):
        return self.value


class VideoDefinitionFilter(Enum):
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
    channel_type: Union[ChannelTypeFilter, str] = None
    event_type: Union[str, EventTypeFilter] = None
    order: Union[str, OrderFilter] = None
    safe_search: Union[str, SafeSearchFilter] = None
    _type: Union[str, type[Union[YoutubeVideo, YoutubeChannel, YoutubePlaylist]]] = None
    video_caption: Union[str, VideoCaptionFilter] = None
    video_definition: Union[str, VideoDefinitionFilter] = None
    video_dimension: Union[str, VideoDimensionFilter] = None
    video_duration: Union[str, VideoDurationFilter] = None
    video_embeddable: Union[str, VideoEmbeddableFilter] = None
    video_license: Union[str, VideoLicenseFilter] = None
    video_paid_product_placement: Union[str, VideoPaidProductPlacementFilter] = None
    video_syndicated: Union[str, VideoSyndicatedFilter] = None
    video_type: Union[str, VideoTypeFilter] = None
