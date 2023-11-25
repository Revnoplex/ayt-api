import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Union
from .types import YoutubeVideo, YoutubeChannel, YoutubePlaylist


class ChannelTypeFilter(Enum):
    """Restrict a search to a particular type of channel (e.g. show)."""

    show = "show"
    any = "any"

    def __str__(self):
        return self.value


class EventTypeFilter(Enum):
    """Restricts a search to broadcast events."""

    completed = "completed"
    live = "live"
    upcoming = "upcoming"

    def __str__(self):
        return self.value


class OrderFilter(Enum):
    """Specifies the method that will be used to order resources in the search."""

    date = "date"
    rating = "rating"
    relevance = "relevance"
    title = "title"
    video_count = "view_count"
    view_count = "view_count"

    def __str__(self):
        return self.value


class SafeSearchFilter(Enum):
    """ Whether the search results should include restricted content as well as standard content."""

    moderate = "moderate"
    none = "none"
    strict = "strict"

    def __str__(self):
        return self.value


class VideoCaptionFilter(Enum):
    """Show results based on whether videos have captions."""

    closed_caption = "closed_caption"
    none = "none"
    any = "any"

    def __str__(self):
        return self.value


class VideoDimensionFilter(Enum):
    """Restrict a search to only retrieve 2D or 3D videos."""

    _2d = "2d"
    _3d = "3d"
    any = "any"

    def __str__(self):
        return self.value


class VideoDurationFilter(Enum):
    """Show videos based on their duration."""

    long = "long"
    medium = "medium"
    short = "short"
    any = "any"

    def __str__(self):
        return self.value


class VideoEmbeddableFilter(Enum):
    """Restrict a search to only videos that can be embedded into a webpage."""

    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoPaidProductPlacementFilter(Enum):
    """Restrict a search to only show videos that the creator has denoted as having a paid promotion."""

    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoSyndicatedFilter(Enum):
    """Restrict a search to only videos that can be played outside YouTube."""

    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoTypeFilter(Enum):
    """Restrict a search to a particular type of videos."""

    episode = "episode"
    movie = "movie"
    any = "any"

    def __str__(self):
        return self.value


class VideoLicenseFilter(Enum):
    """Restrict a search to only show videos that use the particular license specified."""

    creative_common = "creative_common"
    youtube = "youtube"
    any = "any"

    def __str__(self):
        return self.value


class VideoDefinitionFilter(Enum):
    """Restrict a search to only show videos with the specified definition."""

    high = "high"
    standard = "standard"
    any = "any"

    def __str__(self):
        return self.value


@dataclass
class SearchFilter:
    """Filters a search result.

    All filter names that start with "video" as well as :param:`event_type` must also have :param:`_type` set to
    :class:`YoutubeVideo` for the request to be valid or a :class:`HTTPException`
    will be raised due the API returning a 400 status code error.

    Attributes:
        channel_id (Optional[str]): Show results related to a certain channel.
        published_after (Union[str, int, datetime.datetime, None]): Show results at or after the specified date.
        published_before (Union[str, int, datetime.datetime, None]): Show results at or before the specified date.
        region_code (Optional[str]): Show results that can be viewed in the specific country specified in the
            ISO 3166-1 alpha-2 code.
        relevance_language (Optional[str]): Show results most relevant to the specified language as a ISO639-1 code.
        topic_id (Optional[str]): Show results associated with the specified topic.
        video_category_id (Optional[str]): Filters video search results based on their category. The :param:`_type`
            filter must be also be set to :class:`YoutubeVideo`.
        channel_type (Union[ChannelTypeFilter, str, None]): Restrict a search to a particular type of channel
            (e.g. show).
        event_type (Union[str, EventTypeFilter, None]): Restricts a search to broadcast events. The :param:`_type`
            filter must be also be set to :class:`YoutubeVideo`.
        order (Union[str, OrderFilter, None]): Specifies the method that will be used to order resources in the search.
            The method is relevance.
        safe_search (Union[str, SafeSearchFilter, None]): Whether the search results should include restricted content
            as well as standard content.
        _type (Union[str, type[Union[YoutubeVideo, YoutubeChannel, YoutubePlaylist]], None]): Restricts a search
            to only a particular type of resource. Defaults to all (no restrictions).
        video_caption (Union[str, VideoCaptionFilter, None]): Show results based on whether videos have captions.
            The :param:`_type` filter must be also be set to :class:`YoutubeVideo`.
        video_definition (Union[str, VideoDefinitionFilter, None]): Restrict a search to only show videos with the
            specified definition. The :param:`_type` filter must be also be set to :class:`YoutubeVideo`.
        video_dimension (Union[str, VideoDimensionFilter, None]): Restrict a search to only retrieve 2D or 3D videos.
            The :param:`_type` filter must be also be set to :class:`YoutubeVideo`.
        video_duration (Union[str, VideoDurationFilter, None]): Show videos based on their duration.
            The :param:`_type` filter must be also be set to :class:`YoutubeVideo`.
        video_embeddable (Union[str, VideoEmbeddableFilter, None]): Restrict a search to only videos that can be
            embedded into a webpage. The :param:`_type` filter must be also be set to :class:`YoutubeVideo`.
        video_license (Union[str, VideoLicenseFilter, None]): Restrict a search to only show videos that use the
            particular license specified. The :param:`_type` filter must be also be set to :class:`YoutubeVideo`.
        video_paid_product_placement (Union[str, VideoPaidProductPlacementFilter, None]): Restrict a search to only
            show videos that the creator has denoted as having a paid promotion. The :param:`_type` filter must be also
            be set to :class:`YoutubeVideo`.
        video_syndicated (Union[str, VideoSyndicatedFilter, None]): Restrict a search to only videos that can be
            played outside YouTube. The :param:`_type` filter must be also be set to :class:`YoutubeVideo`.
        video_type (Union[str, VideoTypeFilter, None]): Restrict a search to a particular type of videos.
            The :param:`_type` filter must be also be set to :class:`YoutubeVideo`.
    """

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
