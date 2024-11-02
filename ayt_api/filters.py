import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Union
from .types import YoutubeVideo, YoutubeChannel, YoutubePlaylist


class ChannelTypeFilter(Enum):
    """
    Restrict a search to a particular type of channel (e.g. show).

    Attributes:
        any: Return all channels.
        show: Only retrieve shows.
    """

    show = "show"
    any = "any"

    def __str__(self):
        return self.value


class EventTypeFilter(Enum):
    """
    Restricts a search to broadcast events.

    Attributes:
        completed: Only include completed broadcasts.
        live: Only include active broadcasts.
        upcoming: Only include upcoming broadcasts.
    """

    completed = "completed"
    live = "live"
    upcoming = "upcoming"

    def __str__(self):
        return self.value


class OrderFilter(Enum):
    """
    Specifies the method that will be used to order resources in the search.

    Attributes:
        date: Resources are sorted in reverse chronological order based on the date they were created.
        rating: Resources are sorted from highest to lowest rating.
        relevance: Resources are sorted based on their relevance to the search query. This is the default value for
            this parameter.
        title: Resources are sorted alphabetically by title.
        video_count: Channels will be sorted in descending order of their number of uploaded videos.
        view_count: Resources will be sorted from highest to lowest number of views. For live broadcasts, videos are
            sorted by number of concurrent viewers while the broadcasts are ongoing.
    """

    date = "date"
    rating = "rating"
    relevance = "relevance"
    title = "title"
    video_count = "view_count"
    view_count = "view_count"

    def __str__(self):
        return self.value


class SafeSearchFilter(Enum):
    """
    Whether the search results should include restricted content as well as standard content.

    Attributes:
        moderate: YouTube will filter some content from search results and, at the least, will filter content that is
            restricted in your locale. Based on their content, search results could be removed from search results or
            demoted in search results. This is the default parameter value.
        none: YouTube will not filter the search result set.
        strict: YouTube will try to exclude all restricted content from the search result set. Based on their content,
            search results could be removed from search results or demoted in search results.
    """

    moderate = "moderate"
    none = "none"
    strict = "strict"

    def __str__(self):
        return self.value


class VideoCaptionFilter(Enum):
    """
    Show results based on whether videos have captions.

    Attributes:
        any: Do not filter results based on caption availability.
        closed_caption: Only include videos that have captions.
        none: Only include videos that do not have captions.
    """

    closed_caption = "closed_caption"
    none = "none"
    any = "any"

    def __str__(self):
        return self.value


class VideoDimensionFilter(Enum):
    """
    Restrict a search to only retrieve 2D or 3D videos.

    Attributes:
        _2d: Restrict search results to exclude 3D videos.
        _3d: Restrict search results to only include 3D videos.
        any: Include both 3D and non-3D videos in returned results. This is the default value.
    """

    _2d = "2d"
    _3d = "3d"
    any = "any"

    def __str__(self):
        return self.value


class VideoDurationFilter(Enum):
    """
    Show videos based on their duration.

    Attributes:
        any: Do not filter video search results based on their duration. This is the default value.
        long: Only include videos longer than 20 minutes.
        medium: Only include videos that are between four and 20 minutes long (inclusive).
        short: Only include videos that are less than four minutes long.
    """

    long = "long"
    medium = "medium"
    short = "short"
    any = "any"

    def __str__(self):
        return self.value


class VideoEmbeddableFilter(Enum):
    """
    Restrict a search to only videos that can be embedded into a webpage.

    Attributes:
        any: Return all videos, embeddable or not.
        true: Only retrieve embeddable videos.
    """

    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoPaidProductPlacementFilter(Enum):
    """
    Restrict a search to only show videos that the creator has denoted as having a paid promotion.

    Attributes:
        any: Return all videos, regardless of whether they contain paid promotions.
        true: Only retrieve videos with paid promotions.
    """

    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoSyndicatedFilter(Enum):
    """
    Restrict a search to only videos that can be played outside YouTube.

    Attributes:
        any: Return all videos, syndicated or not.
        true: Only retrieve syndicated videos.
    """

    true = "true"
    any = "any"

    def __str__(self):
        return self.value


class VideoTypeFilter(Enum):
    """
    Restrict a search to a particular type of videos.

    Attributes:
        any: Return all videos.
        episode: Only retrieve episodes of shows.
        movie: Only retrieve movies.
    """

    episode = "episode"
    movie = "movie"
    any = "any"

    def __str__(self):
        return self.value


class VideoLicenseFilter(Enum):
    """
    Restrict a search to only show videos that use the particular license specified.

    Attributes:
        any: Return all videos, regardless of which license they have, that match the query parameters.
        creative_common: Only return videos that have a Creative Commons license. Users can reuse videos with this
            license in other videos that they create. Learn more.
        youtube: Only return videos that have the standard YouTube license.
    """

    creative_common = "creative_common"
    youtube = "youtube"
    any = "any"

    def __str__(self):
        return self.value


class VideoDefinitionFilter(Enum):
    """
    Restrict a search to only show videos with the specified definition.

    Attributes:
        any: Return all videos, regardless of their resolution.
        high: Only retrieve HD videos.
        standard: Only retrieve videos in standard definition.
    """

    high = "high"
    standard = "standard"
    any = "any"

    def __str__(self):
        return self.value


@dataclass
class SearchFilter:
    """Filters a search result.

    Note:
        All filter names that start with "video" as well as ``event_type`` must also have ``kind`` set to
        :class:`YoutubeVideo` for the request to be valid or a :class:`HTTPException`
        will be raised due the API returning a `400 <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400>`_
        status code error.

    Attributes:
        channel_id (Optional[str]): Show results related to a certain channel.
        published_after (Union[str, int, datetime.datetime, None]): Show results at or after the specified date.
        published_before (Union[str, int, datetime.datetime, None]): Show results at or before the specified date.
        region_code (Optional[str]): Show results that can be viewed in the specific country specified in the
            ISO 3166-1 alpha-2 code.
        relevance_language (Optional[str]): Show results most relevant to the specified language as a ISO639-1 code.
        topic_id (Optional[str]): Show results associated with the specified topic.
        video_category_id (Optional[str]): Filters video search results based on their category. The ``kind``
            filter must be also be set to :class:`YoutubeVideo`.
        channel_type (Union[ChannelTypeFilter, str, None]): Restrict a search to a particular type of channel
            (e.g. show).
        event_type (Union[str, EventTypeFilter, None]): Restricts a search to broadcast events. The ``kind``
            filter must be also be set to :class:`YoutubeVideo`.
        order (Union[str, OrderFilter, None]): Specifies the method that will be used to order resources in the search.
            The method is relevance.
        safe_search (Union[str, SafeSearchFilter, None]): Whether the search results should include restricted content
            as well as standard content.
        kind (Union[str, type[Union[YoutubeVideo, YoutubeChannel, YoutubePlaylist]], None]): Restricts a search
            to only a particular kind of resource. Defaults to all (no restrictions).

            .. versionchanged:: 0.4.0
                Renamed from ``_type``

        video_caption (Union[str, VideoCaptionFilter, None]): Show results based on whether videos have captions.
            The ``kind`` filter must be also be set to :class:`YoutubeVideo`.
        video_definition (Union[str, VideoDefinitionFilter, None]): Restrict a search to only show videos with the
            specified definition. The ``kind`` filter must be also be set to :class:`YoutubeVideo`.
        video_dimension (Union[str, VideoDimensionFilter, None]): Restrict a search to only retrieve 2D or 3D videos.
            The ``kind`` filter must be also be set to :class:`YoutubeVideo`.
        video_duration (Union[str, VideoDurationFilter, None]): Show videos based on their duration.
            The ``kind`` filter must be also be set to :class:`YoutubeVideo`.
        video_embeddable (Union[str, VideoEmbeddableFilter, None]): Restrict a search to only videos that can be
            embedded into a webpage. The ``kind`` filter must be also be set to :class:`YoutubeVideo`.
        video_license (Union[str, VideoLicenseFilter, None]): Restrict a search to only show videos that use the
            particular license specified. The ``kind`` filter must be also be set to :class:`YoutubeVideo`.
        video_paid_product_placement (Union[str, VideoPaidProductPlacementFilter, None]): Restrict a search to only
            show videos that the creator has denoted as having a paid promotion. The ``kind`` filter must be also
            be set to :class:`YoutubeVideo`.
        video_syndicated (Union[str, VideoSyndicatedFilter, None]): Restrict a search to only videos that can be
            played outside YouTube. The ``kind`` filter must be also be set to :class:`YoutubeVideo`.
        video_type (Union[str, VideoTypeFilter, None]): Restrict a search to a particular type of videos.
            The ``kind`` filter must be also be set to :class:`YoutubeVideo`.
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
    kind: Union[str, type[Union[YoutubeVideo, YoutubeChannel, YoutubePlaylist]]] = None
    video_caption: Union[str, VideoCaptionFilter] = None
    video_definition: Union[str, VideoDefinitionFilter] = None
    video_dimension: Union[str, VideoDimensionFilter] = None
    video_duration: Union[str, VideoDurationFilter] = None
    video_embeddable: Union[str, VideoEmbeddableFilter] = None
    video_license: Union[str, VideoLicenseFilter] = None
    video_paid_product_placement: Union[str, VideoPaidProductPlacementFilter] = None
    video_syndicated: Union[str, VideoSyndicatedFilter] = None
    video_type: Union[str, VideoTypeFilter] = None
