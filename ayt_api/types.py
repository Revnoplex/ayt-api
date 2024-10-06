import datetime
import os
import re
import shlex
from dataclasses import dataclass
from typing import Union, Optional, Any
import isodate
from .exceptions import MissingDataFromMetadata
from .utils import camel_to_snake
from .enums import *

VIDEO_URL = "https://www.youtube.com/watch?v={}"
PLAYLIST_URL = "https://www.youtube.com/playlist?list={}"
CHANNEL_URL = "https://www.youtube.com/channel/{}"
HIGHLIGHT_URL = "{0}&lc={1}"
HIGHLIGHT_URL_ID = VIDEO_URL.format("{0}") + "&lc={1}"


@dataclass
class YoutubeThumbnail:
    """Data for an individual YouTube thumbnail.

    Attributes:
        url (Optional[str]): The file url for the thumbnail.
        width (Optional[int]): The amount of horizontal pixels in the thumbnail.
        height (Optional[int]): The amount of vertical pixels in the thumbnail.
        resolution (str): The Width x Height of the thumbnail.
        size (str): An alias of resolution
    """
    url: Optional[str]
    _call_data: Any
    width: Optional[int] = None
    height: Optional[int] = None

    def __post_init__(self):
        self.resolution = "{}x{}".format(self.width, self.height)
        self.size = self.resolution

    def __str__(self):
        return self.url

    async def download(self):
        """Downloads the thumbnail and stores it as a :class:`bytes` object
        Returns:
            bytes: The image as a :class:`bytes` object
        Raises:
            HTTPException: Fetching the request failed.
            aiohttp.ClientError: There was a problem sending the request to the api.
            RuntimeError: The contents was not a jpeg image
            asyncio.TimeoutError: The i.ytimg.com server did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.download_thumbnail(self.url)

    async def save(self, fp: str | os.PathLike | None = None):
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        await self._call_data.save_thumbnail(self.url, fp)


@dataclass
class YoutubeBanner:
    """Data for an individual YouTube thumbnail.

    Attributes:
        url (Optional[str]): The file url for the banner.
    """
    url: Optional[str]
    _call_data: Any

    def __str__(self):
        return self.url

    async def download(self):
        # noinspection SpellCheckingInspection
        """Downloads the banner and stores it as a :class:`bytes` object
                Returns:
                    tuple[bytes, str]: A list containing the image as a :class:`bytes` object and the file extension of
                        the image
                Raises:
                    HTTPException: Fetching the request failed.
                    aiohttp.ClientError: There was a problem sending the request to the api.
                    RuntimeError: The contents was not a jpeg image
                    asyncio.TimeoutError: The yt3.googleusercontent.com server did not respond within the timeout
                        period set.
                """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.download_banner(self.url)

    async def save(self, fp: str | os.PathLike | None = None):
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        await self._call_data.save_banner(self.url, fp)


class YoutubeThumbnailMetadata:
    """
    Data for the available thumbnails of a video.

    Attributes:
        metadata (dict): The raw thumbnail metadata to construct the class.
        available (tuple[str]): Tells what thumbnails are available with the video
    """

    def __init__(self, thumbnail_metadata: dict, call_data):
        """
        Args:
            thumbnail_metadata (dict): The raw thumbnail metadata to construct the class.
            call_data (AsyncYoutubeAPI): Call data used for fetch functions.
        """
        self.metadata = thumbnail_metadata
        self.available = tuple(self.metadata.keys())
        self._call_data = call_data

    def __str__(self):
        return f"Available Resolutions: {', '.join(self.available)}"

    def __repr__(self):
        return f"YoutubeThumbnailMetadata(default={repr(self.default)},medium={repr(self.medium)}," \
               f"high={repr(self.high)},standard={repr(self.standard)},maxres={repr(self.maxres)})"

    def highest_available(self) -> Optional[str]:
        """
        Helper function to get the highest resolution out of the thumbnails available

        Returns:
            Optional[str]: The name of the highest available thumbnail format
        """
        def get_size(thumbnail_code):
            thumbnail_object = getattr(self, thumbnail_code)
            return thumbnail_object.height * thumbnail_object.width
        if self.available:
            return max(self.available, key=get_size)

    @property
    def highest(self) -> Optional[YoutubeThumbnail]:
        """
        Helper property that provided the highest resolution out of the thumbnails available

        Returns:
            Optional[YoutubeThumbnail]: The thumbnail with the highest resolution available
        """
        return getattr(self, self.highest_available()) if self.highest_available() else None

    @property
    def default(self) -> Optional[YoutubeThumbnail]:
        """The default video thumbnail. The value is not guaranteed and could be ``None``.

        This is the most guaranteed to actually return a thumbnail.

        Returns:
            Optional[YoutubeThumbnail]: A YouTube thumbnail object. Could be ``None``.
        """
        if self.metadata.get("default") is not None:
            return YoutubeThumbnail(**self.metadata["default"], _call_data=self._call_data)

    @property
    def medium(self) -> Optional[YoutubeThumbnail]:
        """The medium video thumbnail. The value is not guaranteed and could be ``None``.

        Returns:
            Optional[YoutubeThumbnail]: A YouTube thumbnail object. Could be ``None``.
        """
        if self.metadata.get("medium") is not None:
            return YoutubeThumbnail(**self.metadata["medium"], _call_data=self._call_data)

    @property
    def high(self) -> Optional[YoutubeThumbnail]:
        """The high video thumbnail. The value is not guaranteed and could be ``None``.

        Returns:
            Optional[YoutubeThumbnail]: A YouTube thumbnail object. Could be ``None``.
        """
        if self.metadata.get("high") is not None:
            return YoutubeThumbnail(**self.metadata["high"],  _call_data=self._call_data)

    @property
    def standard(self) -> Optional[YoutubeThumbnail]:
        """The standard video thumbnail. The value is not guaranteed and could be ``None``.

        Returns:
            Optional[YoutubeThumbnail]: A YouTube thumbnail object. Could be ``None``.
        """
        if self.metadata.get("standard") is not None:
            return YoutubeThumbnail(**self.metadata["standard"], _call_data=self._call_data)

    @property
    def maxres(self) -> Optional[YoutubeThumbnail]:
        """The maximum resolution video thumbnail. The value is not guaranteed and could be ``None``.

        Returns:
            Optional[YoutubeThumbnail]: A YouTube thumbnail object. Could be ``None``.
        """
        if self.metadata.get("maxres") is not None:
            return YoutubeThumbnail(**self.metadata["maxres"], _call_data=self._call_data)


@dataclass
class LocalName:
    """Represents the video title and description in a local language if available.

    Attributes:
        language (Optional[str]): The language code.
        title (str): The title in a local language.
        description (Optional[str]): The description in a local language.
    """
    title: str
    description: str = None
    language: str = None


@dataclass
class RegionRestrictions:
    """Represents information about the countries where a video is (or is not) viewable.

    Attributes:
        allowed (Optional[list[str]]): The countries that are allowed to view the video. Could be ``None``.
        blocked (Optional[list[str]]): The countries that are blocked from viewing the video. Could be ``None``.
    """
    allowed: list[str] = None
    blocked: list[str] = None


class ContentRating:
    """Specifies the ratings that the video received under various rating schemes.

        There are many attributes for each rating system, only 1 or 2 (if there is a reason) will be available,
        the rest will be ``None`` or all if there is no restrictions set. The attributes documented below are
        non-exhaustive.

    Attributes:
        acb (Optional[AcbRating]): The video's Australian Classification Board (ACB) or Australian Communications and
            Media Authority (ACMA) rating. ACMA ratings are used to classify children's television programming.
        youtube (Optional[str]): A rating that YouTube uses to identify age-restricted content.
    """
    def __init__(self, data: dict):
        """
        Args:
            data(dict): The raw content rating data.
        """
        self.acb: Optional[AcbRating] = AcbRating(camel_to_snake(data["acbRating"])) if data.get("acbRating") else None
        self.agcom: Optional[str] = data.get("agcomRating")
        self.anatel: Optional[str] = data.get("anatelRating")
        self.bbfc: Optional[str] = data.get("bbfcRatingRating")
        self.bfvc: Optional[str] = data.get("bfvcRatingRating")
        self.bmukk: Optional[str] = data.get("bmukkRatingRating")
        self.catv: Optional[str] = data.get("catvRatingRating")
        self.catvfr: Optional[str] = data.get("catvfrRatingRating")
        self.cbfc: Optional[str] = data.get("cbfcRatingRating")
        self.ccc: Optional[str] = data.get("cccRatingRating")
        self.cce: Optional[str] = data.get("cceRatingRating")
        self.chfilm: Optional[str] = data.get("chfilmRatingRating")
        self.chvrs: Optional[str] = data.get("chvrsRatingRating")
        self.cicf: Optional[str] = data.get("cicfRatingRating")
        self.cna: Optional[str] = data.get("cnaRatingRating")
        self.cnc: Optional[str] = data.get("cncRatingRating")
        self.csa: Optional[str] = data.get("csaRatingRating")
        self.cscf: Optional[str] = data.get("cscfRatingRating")
        self.czfilm: Optional[str] = data.get("czfilmRatingRating")
        self.djctq: Optional[str] = data.get("djctqRatingRating")
        self.djctq_rating_reasons: Optional[list[str]] = data.get("djctqRatingReasons")
        self.ecbmct: Optional[str] = data.get("ecbmctRating")
        self.eefilm: Optional[str] = data.get("eefilmRating")
        self.egfilm: Optional[str] = data.get("egfilmRating")
        self.eirin: Optional[str] = data.get("eirinRating")
        self.fcbm: Optional[str] = data.get("fcbmRating")
        self.fco: Optional[str] = data.get("fcoRating")
        self.fpb: Optional[str] = data.get("fpbRating")
        self.fpb_rating_reasons: Optional[list[str]] = data.get("fpbRatingReasons")
        self.fsk: Optional[str] = data.get("fskRating")
        self.grfilm: Optional[str] = data.get("grfilmRating")
        self.icaa: Optional[str] = data.get("icaaRating")
        self.ifco: Optional[str] = data.get("ifcoRating")
        self.ilfilm: Optional[str] = data.get("ilfilmRating")
        self.incaa: Optional[str] = data.get("incaaRating")
        self.kfcb: Optional[str] = data.get("kfcbRating")
        self.kijkwijzer: Optional[str] = data.get("kijkwijzerRating")
        self.kmrb: Optional[str] = data.get("kmrbRating")
        self.lsf: Optional[str] = data.get("lsfRating")
        self.mccaa: Optional[str] = data.get("mccaaRating")
        self.mccyp: Optional[str] = data.get("mccypRating")
        self.mcst: Optional[str] = data.get("mcstRating")
        self.mda: Optional[str] = data.get("mdaRating")
        self.medietilsynet: Optional[str] = data.get("medietilsynetRating")
        self.meku: Optional[str] = data.get("mekuRatingRating")
        self.mibac: Optional[str] = data.get("mibacRating")
        self.moc: Optional[str] = data.get("mocRating")
        self.moctw: Optional[str] = data.get("moctwRating")
        self.mpaa: Optional[str] = data.get("mpaaRating")
        self.mpaat: Optional[str] = data.get("mpaatRating")
        self.mtrcb: Optional[str] = data.get("mtrcbRating")
        self.nbc: Optional[str] = data.get("nbcRating")
        self.nfrc: Optional[str] = data.get("nfrcRating")
        self.nfvcb: Optional[str] = data.get("nfvcbRating")
        self.nkclv: Optional[str] = data.get("nkclvRating")
        self.oflc: Optional[str] = data.get("oflcRating")
        self.pefilm: Optional[str] = data.get("pefilmRating")
        self.resorteviolencia: Optional[str] = data.get("resorteviolenciaRating")
        self.rtc: Optional[str] = data.get("rtcRating")
        self.rte: Optional[str] = data.get("rteRating")
        self.russia: Optional[str] = data.get("russiaRating")
        self.skfilm: Optional[str] = data.get("skfilmRating")
        self.smais: Optional[str] = data.get("smaisRating")
        self.smsa: Optional[str] = data.get("smsaRating")
        self.tvpg: Optional[str] = data.get("tvpgRating")
        self.youtube: Optional[str] = data.get("ytRating")


@dataclass
class RecordingLocation:
    """The geolocation information associated with the video. if specified by the video uploader.

    Attributes:
        latitude (float): Latitude in degrees.
        longitude (float): Longitude in degrees.
        altitude (float): Altitude above the reference ellipsoid, in meters.
    """
    latitude: float
    longitude: float
    altitude: float


class RecordingDetails:
    """Contains details of the location and date of the video recording if specified by the video uploader.

    Attributes:
        data (dict): The raw information about the location, date and address where the video was recorded.
        description (Optional[str]): The text description of the location where the video was recorded.
        location (Optional[RecordingLocation]): The geolocation information associated with the video.
        date (Optional[datetime.datetime]): The date and time when the video was recorded.
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw recording details used to construct this class.
        """
        self.data = data
        self.description: Optional[str] = data.get("locationDescription")
        if data.get("location") is None:
            self.location: Optional[RecordingLocation] = None
        else:
            self.location: Optional[RecordingLocation] = RecordingLocation(**data["location"])
        if data.get("recordingDate") is None:
            self.date: Optional[datetime.datetime] = None
        else:
            self.date: Optional[datetime.datetime] = isodate.parse_datetime(data["recordingDate"])


class VideoStream:
    """Metadata about a video stream for a YouTube video.

    Attributes:
        data (dict): The raw video stream data used to construct this class.
        width (int): The encoded video content's width in pixels.
        height (int): The encoded video content's height in pixels.
        resolution (str): width x height.
        frame_rate (float): The video stream's frame rate, in frames per second.
        aspect_ratio (float): The video content's display aspect ratio.
        codec (string): The video codec that the stream uses.
        bitrate (int): The video stream's bitrate, in bits per second.
        rotation (string): The amount that YouTube needs to rotate the original source content to properly display the
            video.
        vendor (string): A value that uniquely identifies a video vendor. Typically, the value is a four-letter vendor
            code.
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw video stream data.
        """
        try:
            self.data = data
            self.width: int = data["widthPixels"]
            self.height: int = data["heightPixels"]
            self.resolution: str = '{}x{}'.format(self.width, self.height)
            self.frame_rate: float = data["frameRateFps"]
            self.aspect_ratio: float = data["aspectRatio"]
            self.codec: str = data["codec"]
            self.bitrate: int = data["bitrateBps"]
            self.rotation: str = data["rotation"]
            self.vendor: str = data["vendor"]
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), data, missing_snippet_data)


class AudioStream:
    """Metadata about an audio stream for a YouTube video.

    Attributes:
        data (dict): The raw audio stream data used to construct this class.
        channel_count (int): The number of audio channels that the stream contains.
        codec (string): The audio codec that the stream uses.
        bitrate (int): The audio stream's bitrate, in bits per second.
        vendor (string): A value that uniquely identifies a video vendor. Typically, the value is a four-letter
            vendor code.

    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw audio stream data.
        """
        try:
            self.data = data
            self.channel_count: int = data["channelCount"]
            self.codec: str = data["codec"]
            self.bitrate: int = data["bitrateBps"]
            self.vendor: str = data["vendor"]
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), data, missing_snippet_data)


class ProcessingProgress:
    """Contains information about the progress YouTube has made in processing the video.

    Attributes:
        data (dict): The raw processing progress data used to construct this class.
        parts_total (int): An estimate of the total number of parts that need to be processed for the video.
        parts_processed (int): The number of parts of the video that YouTube has already processed.
        time_left (Optional[datetime.timedelta]): An estimate of the amount of time, in milliseconds, that YouTube
            needs to finish processing the video.
        percentage (int): The percentage of the video that has been processed.
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): Raw processing progress.
        """
        self.data = data
        try:
            self.parts_total: int = data["partsTotal"]
            self.parts_processed: int = data["partsProcessed"]
            if data.get('timeLeftMs') is None:
                self.time_left: Optional[datetime.timedelta] = None
            else:
                self.time_left: Optional[datetime.timedelta] = datetime.timedelta(milliseconds=data["timeLeftMs"])
            self.percentage: int = round(self.parts_processed/self.parts_total*100)
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), data, missing_snippet_data)

    def __str__(self):
        if self.time_left is not None:
            return f"Processing {self.parts_processed}/{self.parts_total} " \
                   f"({round(self.parts_processed/self.parts_total*100)}%) ETA: {self.time_left}"
        else:
            return f"Processing {self.parts_processed}/{self.parts_total} " \
                   f"({round(self.parts_processed / self.parts_total * 100)}%)"


class TagSuggestion:
    """
    A list of keyword tags that could be added to the video's metadata to increase the likelihood that users will
        locate your video when searching or browsing on YouTube.

    Attributes:
        data (dict): The raw tag suggestions data used to construct this class.
        tag (str): The keyword tag suggested for the video.
        category_restricts (Optional[list[str]]): A set of video categories for which the tag is relevant.
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw tag suggestions data.
        """
        self.data = data
        self.tag: str = data["tag"]
        self.category_restricts: Optional[list[str]] = data.get("categoryRestricts")

    def __str__(self):
        if self.category_restricts:
            return f'Tag Suggestion: "{self.tag}" with restrictions: {",".join(self.category_restricts)}'
        else:
            return f'Tag Suggestion: "{self.tag}"'


@dataclass
class VideoChapter:
    """
    The start time, duration and name of a YouTube video chapter.

    Attributes:
        start (int): The start time of the chapter in seconds.
        duration: (int): The length of the chapter in seconds.
        name (str): The name of the chapter.
    """
    start: datetime.timedelta
    duration: datetime.timedelta
    name: str

    def __str__(self):
        return self.name


@dataclass
class BaseVideo:
    """
    The base class that all video related objects are inherited from.

    Attributes:
        metadata (dict): The raw metadata from the API response used to construct this class. Intended use is for
                         debugging purposes.
        call_url (str): The url used to call the API. Intended use is for debugging purposes.
        id (str): The ID of the video. Example: "dQw4w9WgXcQ" from the url:
                  "https://www.youtube.com/watch?v=dQw4w9WgXcQ". Look familiar?
        url (str): The URL of the video.
        title (str): The title of the video.
        description (str): The description of the video.
        thumbnails (YoutubeThumbnailMetadata): The available thumbnails the video has.
        visibility (PrivacyStatus): The video's privacy status. Can be :attr:`PrivacyStatus.private`,
            :attr:`PrivacyStatus.public` or :attr:`PrivacyStatus.unlisted`.

    """
    metadata: dict
    call_url: str
    id: str
    url: str
    title: str
    description: str
    thumbnails = YoutubeThumbnailMetadata
    visibility: PrivacyStatus


class DummyObject:
    """This is used for debugging only."""
    def __init__(self, metadata: dict, call_url: str, call_data):
        self.metadata = metadata
        self.call_url = call_url
        self.call_data = call_data


class YoutubeVideo(BaseVideo):
    """A data class containing video data such as the title, id, description, channel, etc.

    Attributes:
        metadata (dict): The raw metadata from the API response used to construct this class. Intended use is for
                     debugging purposes.
        call_url (str): The url used to call the API. Intended use is for debugging purposes.
        id (str): The ID of the video. Example: "dQw4w9WgXcQ" from the url:
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ". Look familiar?
        snippet (dict): The raw snippet data used to construct part this class.
        content_details (dict): The raw content details data used to construct part of this class.
        status (dict): The raw status data used to construct part of this class.
        statistics (dict): The raw statistics data used to construct part of this class.
        player (dict): The raw player data used to construct part of this class.
        topic_details (Optional[dict]): The raw topic details used to construct part of this class.
        raw_recording_details (dict): The raw recording details used to construct part of this class.
        raw_localisations (Optional[dict]): The raw localisation data used to construct part of this class.
        url (str): The URL of the video.
        title (str): The title of the video.
        description (str): The description of the video.
        published_at (datetime.datetime): The date and time the video was published.
        thumbnails (YoutubeThumbnailMetadata): The available thumbnails the video has.
        channel_title: (Optional[str]) The name of the channel that the video belongs to.
        channel_id (Optional[str]): The id of the channel that the video belongs to.
        channel_url (Optional[str]): The url of the channel that the video belongs to.
        tags (Optional[list[str]]): The tags the uploaded has provided to make the video appear in search results
            relating to it.
        category_id (int): The id of the category that was set for the video.
        live_broadcast_content: (LiveBroadcastContent): Indicates if the video is a livestream and if it is live.
        default_language (Optional[str]): The default language the video is set in.
            The value is a BCP-47 language code.
        localised (Optional[LocalName]): The localised language of the title and description of the video.
        localized (Optional[LocalName]): an alias of :attr:`localised`.
        default_audio_language (Optional[str]): The default audio language the video is set in.
            The value is a BCP-47 language code.
        duration (Union[isodate.Duration, datetime.timedelta, _NotImplementedType]): The length of the video.
        dimension (str): Indicates whether the video is available in 3D or in 2D.
        definition (VideoDefinition): Indicates whether the video is available in high definition (HD) or only in
            standard definition.
        has_captions (bool): Indicates whether captions are available for the video.
        licensed_content (bool): Indicates whether the video represents licensed content, which means that the
            content was uploaded to a channel linked to a YouTube content partner and then claimed by that partner.
        region_restrictions (Optional[RegionRestrictions]): contains information about the countries where a video
            is (or is not) viewable. Can be ``None``.
        content_rating (ContentRating): Specifies the ratings that the video received under various rating schemes.
        age_restricted (bool): Whether the video is age restricted or not.
        projection (Optional[VideoProjection]): Specifies the projection format of the video
            (example: 360 or rectangular).
        upload_status (Optional[UploadStatus]): The status of the uploaded video.
        failure_reason (Optional[UploadFailureReason]): Explains why a video failed to upload.
            This attribute is only present if the upload_status attribute is set to :class:`UploadStatus.failed`.
        rejection_reason (Optional[UploadRejectionReason]): Explains why YouTube rejected an uploaded video.
            This attribute is only present if the upload_status attribute is set to :class:`UploadStatus.rejected`.
        visibility (PrivacyStatus): The video's privacy status. Can be :attr:`PrivacyStatus.private`,
            :attr:`PrivacyStatus.public` or :attr:`PrivacyStatus.unlisted`.
        publish_set_at (Optional[datetime.datetime]): The date and time when the video is scheduled to publish if
            any.
        license (Optional[License]): The video's license. valid values for this attribute is
            :class:`License.creative_common` and :class:`License.youtube`.
        embeddable (bool): Indicates whether the video can be embedded on another website.
        public_stats_viewable (bool): Indicates whether the extended video statistics on the video's watch page are
            publicly viewable.
        made_for_kids (bool): Indicates whether the video is designated as child-directed, and it contains the
            current "made for kids" status of the video.
        view_count (int): The number of times the video has been viewed.
        like_count (Optional[int]): The number of users who have indicated that they liked the video.
        comment_count (Optional[int]): The number of comments on the video. This attribute is ``None`` if disabled
        embed_html (Optional[str]): An <iframe> tag that embeds a player that plays the video.
        embed_height (Optional[str]): The height of the embedded player returned to the embed_html attribute.
            Is ``None`` unless the height and aspect ratio is known.
        embed_width (Optional[str]): The width of the embedded player returned to the embed_html attribute.
            Is ``None`` unless the width and aspect ratio is known.
        topic_categories (Optional[list[str]]): A list of Wikipedia URLs that provide a high-level description of
            the video's content.
        recording_details (RecordingDetails): Encapsulates information about the location, date and address where
            the video was recorded.
        stream_actual_start_time (Optional[datetime.datetime]): The time that the broadcast actually started.
        stream_scheduled_start_time (Optional[datetime.datetime]): The time that the broadcast is scheduled to
            begin.
        stream_actual_end_time (Optional[datetime.datetime]): The time that the broadcast actually ended.
        stream_scheduled_end_time (Optional[datetime.datetime]): The time that the broadcast is scheduled to end.
        stream_concurrent_viewers (Optional[int]): The number of viewers currently watching the broadcast.
        stream_active_live_chat_id (Optional[str]): The ID of the currently active live chat attached to this video.
        localisations (Optional[list[LocalName]]): Contains translations of the video's metadata.
        localizations (Optional[list[LocalName]]): An alias of localisations.
        """
    def __init__(self, metadata: dict, call_url: str, call_data):
        """
        Args:
            metadata (dict): The raw API response to construct the class.
            call_url (str): The url used to call the API.
            call_data (AsyncYoutubeAPI): Call data used for fetch functions.

        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided.
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self._call_data = call_data
            self.snippet: dict = metadata["snippet"]
            self.content_details: dict = metadata["contentDetails"]
            self.status: dict = metadata["status"]
            self.statistics: dict = metadata["statistics"]
            self.player: dict = metadata["player"]
            self.topic_details: Optional[dict] = metadata.get("topicDetails")
            self.raw_recording_details: dict = metadata["recordingDetails"]
            self.live_streaming_details: dict = metadata.get("liveStreamingDetails")
            self.raw_localisations: Optional[dict] = metadata.get("localizations")
            self.id: str = metadata["id"]
            self.url = VIDEO_URL.format(self.id)
            self.published_at = isodate.parse_datetime(self.snippet["publishedAt"])
            self.channel_id: Optional[str] = self.snippet.get("channelId")
            if self.channel_id is None:
                self.channel_url: Optional[str] = None
            else:
                self.channel_url: Optional[str] = CHANNEL_URL.format(self.channel_id)
            self.title: str = self.snippet["title"]
            self.description: str = self.snippet["description"]
            self.thumbnails = YoutubeThumbnailMetadata(self.snippet["thumbnails"], self._call_data)
            self.channel_title: Optional[str] = self.snippet.get("channelTitle")
            self.tags: Optional[list[str]] = self.snippet.get("tags")
            self.category_id: int = int(self.snippet["categoryId"])
            self.live_broadcast_content: LiveBroadcastContent = \
                LiveBroadcastContent(self.snippet["liveBroadcastContent"])
            self.default_language: Optional[str] = self.snippet.get("defaultLanguage")
            if self.snippet.get("localized") is None:
                self.localized: Optional[LocalName] = None
            else:
                self.snippet["localized"]["language"] = self.default_language
                self.localised: Optional[LocalName] = LocalName(**self.snippet["localized"])
            self.localized = self.localised
            self.default_audio_language: Optional[str] = self.snippet.get("defaultAudioLanguage")
            self.duration = isodate.parse_duration(self.content_details["duration"])
            self.dimension: str = self.content_details["dimension"]
            self.definition: VideoDefinition = VideoDefinition(self.content_details["definition"])
            if self.content_details["caption"] == "true":
                self.has_captions = True
            elif self.content_details["caption"] == "false":
                self.has_captions = False
            else:
                self.has_captions = None
            self.licensed_content: bool = self.content_details["licensedContent"]
            if self.content_details.get("regionRestriction") is None:
                self.region_restrictions: Optional[RegionRestrictions] = None
            else:
                self.region_restrictions: Optional[RegionRestrictions] = \
                    RegionRestrictions(**self.content_details["regionRestriction"])
            self.content_rating = ContentRating(self.content_details["contentRating"])
            self.age_restricted = bool(self.content_rating.youtube)
            self.projection: Optional[VideoProjection] = VideoProjection(self.content_details["projection"]) \
                if self.content_details.get("projection") else None
            self.upload_status: Optional[UploadStatus] = UploadStatus(self.status["uploadStatus"]) \
                if self.status.get("uploadStatus") else None
            self.failure_reason = UploadFailureReason(camel_to_snake(self.status["failureReason"])) \
                if self.status.get("failureReason") else None
            self.rejection_reason = UploadRejectionReason(camel_to_snake(self.status["rejectionReason"])) \
                if self.status.get("rejectionReason") else None
            self.visibility = PrivacyStatus(camel_to_snake(self.status["privacyStatus"]))
            if self.status.get("publishAt") is None:
                self.publish_set_at: Optional[datetime.datetime] = None
            else:
                self.publish_set_at: Optional[datetime.datetime] = isodate.parse_datetime(self.status.get("publishAt"))
            self.license: Optional[str] = License(camel_to_snake(self.status["license"])) \
                if self.status.get("license") else None
            self.embeddable: bool = self.status["embeddable"]
            self.public_stats_viewable: bool = self.status["publicStatsViewable"]
            self.made_for_kids: bool = self.status["madeForKids"]
            self.view_count: int = self.statistics["viewCount"]
            self.like_count: Optional[int] = self.statistics.get("likeCount")
            self.comment_count: Optional[int] = self.statistics.get("commentCount")
            self.embed_html: Optional[str] = self.player.get("embedHtml")
            self.embed_height: Optional[str] = self.player.get("embedHeight")
            self.embed_width: Optional[str] = self.player.get("embedWidth")
            if self.topic_details is None:
                self.topic_categories: Optional[list[str]] = None
            else:
                self.topic_categories: Optional[list[str]] = self.topic_details.get("topicCategories")
            self.recording_details = RecordingDetails(self.raw_recording_details)
            self.stream_actual_start_time: Optional[datetime.datetime] = None
            self.stream_scheduled_start_time: Optional[datetime.datetime] = None
            self.stream_actual_end_time: Optional[datetime.datetime] = None
            self.stream_scheduled_end_time: Optional[datetime.datetime] = None
            self.stream_concurrent_viewers: Optional[int] = None
            self.stream_active_live_chat_id: Optional[str] = None
            if self.live_streaming_details is not None:
                if self.live_streaming_details.get("actualStartTime") is not None:
                    self.stream_actual_start_time: Optional[datetime.datetime] = \
                        isodate.parse_datetime(self.live_streaming_details.get("actualStartTime"))
                if self.live_streaming_details.get("scheduledStartTime") is not None:
                    self.stream_scheduled_start_time: Optional[datetime.datetime] = \
                        isodate.parse_datetime(self.live_streaming_details.get("scheduledStartTime"))
                if self.live_streaming_details.get("actualEndTime") is not None:
                    self.stream_actual_end_time: Optional[datetime.datetime] = \
                        isodate.parse_datetime(self.live_streaming_details.get("actualEndTime"))
                if self.live_streaming_details.get("scheduledEndTime") is not None:
                    self.stream_scheduled_end_time: Optional[datetime.datetime] = \
                        isodate.parse_datetime(self.live_streaming_details.get("scheduledEndTime"))
                self.stream_concurrent_viewers: Optional[int] = self.live_streaming_details.get("concurrentViewers")
                self.stream_active_live_chat_id: Optional[str] = self.live_streaming_details.get("activeLiveChatId")
            if self.duration.total_seconds() < 1 and self.stream_actual_start_time is not None:
                self.duration = \
                    datetime.timedelta(
                        seconds=datetime.datetime.now().timestamp() - self.stream_actual_start_time.timestamp())
            if self.raw_localisations is None:
                self.localisations: Optional[list[LocalName]] = None
            else:
                self.localisations: Optional[list[LocalName]] = []
                for localisation in self.raw_localisations.items():
                    self.localisations.append(LocalName(**localisation[1], language=localisation[0]))
            self.localizations = self.localisations

        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)
        except TypeError as missing_snippet_data:
            missing_str = f"{str(missing_snippet_data).split('arguments: ')[-1]} in " \
                          f"{str(missing_snippet_data).split('.')[0]}"
            raise MissingDataFromMetadata(missing_str, metadata, missing_snippet_data)

    async def fetch_channel(self):
        """Fetches the channel associated with the video.

        This ia an api call which then returns a
        :class:`YoutubeChannelMetadata` object.

        Returns:
            Optional[YoutubeChannelMetadata]: The channel object containing data of the channel.

        Raises:
            HTTPException: Fetching the metadata failed.
            ChannelNotFound: The channel does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        if self.channel_id:
            from .api import AsyncYoutubeAPI
            self._call_data: AsyncYoutubeAPI
            return await self._call_data.fetch_channel(self.channel_id)

    async def fetch_comments(self, max_comments: Optional[int] = 50):
        """Fetches a list of comments on the video.

        This ia an api call which then returns a
        :class:`list[YoutubeCommentThread]` object.

        Returns:
            list[YoutubeCommentThread]: A list of comments on the video.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_video_comments(self.id, max_comments)

    async def fetch_captions(self):
        """Fetches a list of captions on the video.

        This ia an api call which then returns a
        :class:`list[VideoCaptions]` object.

        Returns:
            list[VideoCaptions]: A list of captions on the video.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_video_captions(self.id)

    @property
    def chapters(self) -> Optional[list[VideoChapter]]:
        """A list of chapters the video has if any otherwise just an empty list.

        Returns:
            chapters (list[VideoChapter]): A list of chapters the video has if any otherwise ``None``.
        """
        found_chapters: list[tuple] = []
        for line in reversed(self.description.splitlines()):
            # regex is from https://stackoverflow.com/a/11067610
            parsed = re.search(r'(?:([0-5]?[0-9]):)?([0-5]?[0-9]):([0-5][0-9])', line)
            if parsed is not None:
                raw_stamp = parsed.group()
                split_timestamp = raw_stamp.split(":")
                seconds = 0
                for index, part in enumerate(reversed(split_timestamp)):
                    seconds += int(part) * 60 ** index
                start = datetime.timedelta(seconds=seconds)
                end = found_chapters[-1][0] if len(found_chapters) > 0 else self.duration
                duration = end - start
                line = line.replace(raw_stamp, "", 1).strip(" -\n")
                line = line[:-2].strip() if line.endswith("()") else line
                line = line[2:].strip() if line.startswith("()") else line
                found_chapters.append((start, duration, line))
        return [VideoChapter(*chapter_data) for chapter_data in reversed(found_chapters)] if found_chapters else None

    def current_chapter(self, position: datetime.timedelta) -> Optional[VideoChapter]:
        """
        Gets the current chapter based on the position provided.

        Args:
            position (datetime.timedelta): The position of the video to get the current chapter from.

        Returns:
            Optional[VideoChapter]: The current video chapter at that position of the video. Returns ``None`` if either
                the video doesn't have any chapters or the position is greater than the duration of the video or is
                negative.
        """
        if self.chapters:
            for idx, chapter in enumerate(self.chapters):
                if chapter.start <= position < chapter.start + chapter.duration or \
                        (idx+1 == len(self.chapters) and position == self.duration):
                    return chapter


class PlaylistItem(BaseVideo):
    """A data class for videos in a playlist.

    Attributes:
        metadata (dict): The raw metadata from the API call used to construct this class.
        call_url (str): The url used to call the API. Intended use is for debugging purposes.
        id (str): The ID of the video in the playlist. Example: "dQw4w9WgXcQ" from the url:
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ". Look familiar?
        position (int): The position in the playlist the video is in.
        url (str): The URL of the video.
        title (str): The title of the video.
        description (str): The description of the video.
        added_at (datetime.datetime): The date and time the video was added to the playlist.
        thumbnails (YoutubeThumbnailMetadata): The available thumbnails the video has.
        channel_title: (Optional[str]) The name of the channel that the video belongs to.
        channel_id (Optional[str]): The id of the channel that the video belongs to.
        channel_url (Optional[str]): The url of the channel that the video belongs to.
        playlist_id (str): The ID of the playlist the video is in.
        playlist_url (str): The URL of the playlist the video is in.
        published_at (datetime.datetime): The date and time the video was published.
        available (bool): Whether the video in the playlist is playable hasn't been deleted or made private.
            This is determined by checking if the video has an upload date.
        note (Optional[str]): A user-generated note for this item.
        visibility (PrivacyStatus): The playlist item's privacy status. Can be :attr:`PrivacyStatus.private`,
            :attr:`PrivacyStatus.public` or :attr:`PrivacyStatus.unlisted`.
    """
    def __init__(self, metadata: dict, call_url: str, call_data):
        """
        Args:
            metadata (dict): The raw API response to construct the class.
            call_url (str): The url used to call the API.
            call_data (AsyncYoutubeAPI): call data used for fetch functions.

        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided.
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self._call_data = call_data
            self.snippet: dict = metadata["snippet"]
            self.content_details: dict = metadata["contentDetails"]
            self.status: dict = metadata["status"]
            self.added_at = isodate.parse_datetime(self.snippet["publishedAt"])
            self.position: int = self.snippet["position"]
            self.id: str = self.content_details["videoId"]
            self.url = VIDEO_URL.format(self.id)
            self.title: str = self.snippet.get("title")
            self.description: str = self.snippet.get('description')
            self.thumbnails = YoutubeThumbnailMetadata(self.snippet["thumbnails"], self._call_data)
            self.channel_id: Optional[str] = self.snippet.get("videoOwnerChannelId")
            if self.channel_id is None:
                self.channel_url: Optional[str] = None
            else:
                self.channel_url: Optional[str] = CHANNEL_URL.format(self.channel_id)
            self.channel_title: Optional[str] = self.snippet.get("videoOwnerChannelTitle")
            self.playlist_id: str = self.snippet["playlistId"]
            self.playlist_url = PLAYLIST_URL.format(self.playlist_id)
            self.note: Optional[str] = self.content_details.get("note")
            self.published_at = None if self.content_details.get("videoPublishedAt") is None else \
                isodate.parse_datetime(self.content_details["videoPublishedAt"])
            self.available = bool(self.published_at)
            self.visibility: Optional[PrivacyStatus] = PrivacyStatus(camel_to_snake(self.status["privacyStatus"])) if \
                self.status.get("privacyStatus") else None
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)

    async def expand(self) -> YoutubeVideo:
        """Fetches extended information on the video in the playlist.

        This ia an api call which then returns a
        :class:`YoutubeVideo` object.

        Returns:
            YoutubeVideo The video object containing data of the video.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_video(self.id)

    async def fetch_playlist(self):
        """Fetches the playlist associated with the video.

        This ia an api call which then returns a
        :class:`YoutubePlaylist` object.

        Returns:
            YoutubePlaylist: The playlist object containing data of the playlist.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_playlist(self.playlist_id)

    async def fetch_channel(self):
        """Fetches the channel associated with the video.

        This ia an api call which then returns a
        :class:`YoutubeChannelMetadata` object.

        Returns:
            Optional[YoutubeChannelMetadata]: The channel object containing data of the channel.

        Raises:
            HTTPException: Fetching the metadata failed.
            ChannelNotFound: The channel does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        if self.channel_id:
            from .api import AsyncYoutubeAPI
            self._call_data: AsyncYoutubeAPI
            return await self._call_data.fetch_channel(self.channel_id)

    async def fetch_comments(self, max_comments: Optional[int] = 50):
        """Fetches a list of comments on the video.

        This ia an api call which then returns a
        :class:`list[YoutubeCommentThread]` object.

        Returns:
            list[YoutubeCommentThread]: A list of comments on the video.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_video_comments(self.id, max_comments)

    async def fetch_captions(self):
        """Fetches a list of comments on the video.

        This ia an api call which then returns a
        :class:`list[VideoCaptions]` object.

        Returns:
            list[VideoCaptions]: A list of comments on the video.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_video_captions(self.id)


class YoutubePlaylist:
    """Data class for YouTube playlists.

    Attributes:
        metadata (dict): The raw API response used to construct this class.
        call_url (str): The url used to call the API. Intended use is for debugging purposes.
        id (str): The ID of the playlist. Example: "PLwZcI0zn-Jhemx2m_gpYqQfnc3l4xA4fp" from the url:
            "https://www.youtube.com/playlist?list=PLwZcI0zn-Jhemx2m_gpYqQfnc3l4xA4fp".
        url (str): The URL of the playlist.
        snippet (dict): The raw snippet data used to construct this class.
        status (dict): The raw status data used to construct part of this class.
        content_details (dict): The raw content details data used to construct part of this class.
        player (dict): The raw player data used to construct part of this class.
        raw_localisations (Optional[dict]): The raw localisation data used to construct part of this class.
        published_at (datetime.datetime): The date and time the playlist was published.
        channel_id (Optional[str]): The id of the channel that created the playlist.
        channel_url (Optional[str]): The url of the channel that created the playlist.
        title (str): The title of the playlist.
        description (str): The description of the playlist.
        thumbnails (YoutubeThumbnailMetadata): The available thumbnails the playlist has.
        channel_title: (Optional[str]) The name of the channel that created the playlist.
        default_language (Optional[str]): The default language the video is set in. Can be ``None``.
        localised (Optional[LocalName]): The localised language of the title and description of the video.
        localized (Optional[LocalName]): an alias of :attr:`localised`.
        visibility (Optional[PrivacyStatus]): The video's privacy status. Can be :attr:`PrivacyStatus.private`,
            :attr:`PrivacyStatus.public` or :attr:`PrivacyStatus.unlisted`.
        item_count (Optional[int]): The number of items in the playlist.
        embed_html (Optional[str]): An <iframe> tag that embeds a player that plays the video.
        localisations (Optional[list[LocalName]]): contains translations of the video's metadata.
        localizations (Optional[list[LocalName]]): an alias of :attr:`localisations`.
    """
    def __init__(self, metadata: dict, call_url: str, call_data):
        """
        Args:
            metadata (dict): The raw API response to construct the class.
            call_url (str): The url used to call the API.
            call_data (AsyncYoutubeAPI): call data used for fetch functions.

        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided.
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self._call_data = call_data
            self.id: str = metadata["id"]
            self.url = PLAYLIST_URL.format(self.id)
            self.snippet: dict = metadata["snippet"]
            self.status: dict = metadata["status"]
            self.content_details: dict = metadata["contentDetails"]
            self.player: dict = metadata["player"]
            self.raw_localisations: Optional[dict] = metadata.get("localizations")
            self.published_at = isodate.parse_datetime(self.snippet["publishedAt"])
            self.channel_id: Optional[str] = self.snippet.get("channelId")
            if self.channel_id is None:
                self.channel_url: Optional[str] = None
            else:
                self.channel_url: Optional[str] = CHANNEL_URL.format(self.channel_id)
            self.title: str = self.snippet["title"]
            self.description: str = self.snippet["description"]
            self.thumbnails = YoutubeThumbnailMetadata(self.snippet["thumbnails"], self._call_data)
            self.channel_title: Optional[str] = self.snippet.get("channelTitle")
            self.default_language: Optional[str] = self.snippet.get("defaultLanguage")
            if self.snippet.get("localized") is None:
                self.localised: Optional[LocalName] = None
            else:
                self.snippet["localized"]["language"] = self.default_language
                self.localised: Optional[LocalName] = LocalName(**self.snippet["localized"])
            self.localized = self.localised
            self.visibility: Optional[PrivacyStatus] = PrivacyStatus(camel_to_snake(self.status["privacyStatus"])) if \
                self.status.get("privacyStatus") else None
            self.item_count: Optional[int] = self.content_details.get("itemCount")
            self.embed_html: Optional[str] = self.player.get("embedHtml")
            if self.raw_localisations is None:
                self.localisations: Optional[list[LocalName]] = None
            else:
                self.localisations: Optional[list[LocalName]] = []
                for localisation_name, localisation_value in self.raw_localisations.items():
                    self.localisations.append(LocalName(**localisation_value, language=localisation_name))
            self.localizations = self.localisations
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)

    async def fetch_items(self) -> list[PlaylistItem]:
        """
        Fetches a list of the videos in the playlist.

        This is an api call which returns a list of
        :class:`PlaylistItem` objects.

        Returns:
            list[PlaylistItem]: A list containing playlist video objects.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_playlist_items(self.id)

    async def fetch_videos(self, exclude: list[str] = None) -> list[YoutubeVideo]:
        """
        Fetches a list of the videos in the playlist.

        This is an api call which returns a list of
        :class:`YoutubeVideo` objects.

        Args:
            exclude (Optional[list[str]]): A list of videos to not fetch in the playlist

        Returns:
            list[YoutubeVideo]: A list containing videos from the playlist.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_playlist_videos(self.id, exclude)

    async def fetch_channel(self):
        """Fetches the channel associated with the playlist.

        This ia an api call which then returns a
        :class:`YoutubeChannelMetadata` object.

        Returns:
            Optional[YoutubeChannelMetadata]: The channel object containing data of the channel.

        Raises:
            HTTPException: Fetching the metadata failed.
            ChannelNotFound: The channel does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        if self.channel_id:
            from .api import AsyncYoutubeAPI
            self._call_data: AsyncYoutubeAPI
            return await self._call_data.fetch_channel(self.channel_id)


class AuthorisedYoutubeVideo(YoutubeVideo):
    """
    A data class containing owner only information video data such as the file and processing information.

        This class is used if authorisation is provided that you are the owner of the video. It contains
        attributes only accessible by the video owner as well as attributes inherited
        from :class:`YoutubeVideoMetadata`. The ayt-api library currently doesn't support authorisation for this
        so this class is not used but is here for future implementation.

    Attributes:
        file_details (dict): The raw file details used to construct this class.
        has_custom_thumbnail (bool): Indicates whether the video uploader has provided a custom thumbnail image for
            the video.
        self_declared_made_for_kids (bool): This Attribute allows the channel owner to designate the video as being
                child-directed.
        dislike_count (Optional[int]): The number of users who have indicated that they disliked the video.
        file_name (str): The uploaded file's name.
        file_size (int): The uploaded file's size in bytes.
        file_type (str): The uploaded file's type as detected by YouTube's video processing engine.
        file_container (str): The uploaded video file's container format.
        video_streams (Optional[list[VideoStream]]): A list of video streams contained in the uploaded video file.
        audio_streams (Optional[list[AudioStream]]): A list of audio streams contained in the uploaded video file.
        file_duration (datetime.timedelta): The length of the uploaded video millisecond accurate.
        file_bitrate (int): The uploaded video file's combined (video and audio) bitrate in bits per second.
        file_creation_time (Optional[datetime.datetime]): The date and time when the uploaded video file was created.
        processing_status (Optional[str]): The video's processing status.
        processing_progress (Optional[ProcessingProgress]):
            contains information about the progress YouTube has made in processing the video
        processing_failure_reason (Optional[str]): The reason that YouTube failed to process the video.
        file_details_availability (Optional[str]): This value indicates whether file details are available for the
            uploaded video.
        processing_issues_availability (Optional[str]):
            indicates whether the video processing engine has generated suggestions that might improve YouTube's
            ability to process the video, warnings that explain video processing problems, or errors that cause
            video processing problems.
        tag_suggestions_availability (Optional[str]):
            This value indicates whether keyword (tag) suggestions are available for the video.
        editor_suggestions_availability (Optional[str]):
            This value indicates whether video editing suggestions, which might improve video quality or the playback
            experience, are available for the video.
        thumbnails_availability (Optional[str]): This value indicates whether thumbnail images have been generated for
            the video.
        processing_errors (Optional[list[str]]):
            A list of errors that will prevent YouTube from successfully processing the uploaded video.
        processing_warnings (Optional[list[str]]): A list of reasons why YouTube may have difficulty transcoding the
            uploaded
            video or that might result in an erroneous transcoding.
        processing_hints (Optional[list[str]]): A list of suggestions that may improve YouTube's ability to process the
            video.
        tag_suggestions (Optional[list[TagSuggestion]]):
            A list of keyword tags that could be added to the video's metadata to increase the likelihood that users
            will locate your video when searching or browsing on YouTube.
        editor_suggestions (Optional[list[str]]):
            A list of video editing operations that might improve the video quality or playback experience of the
            uploaded video.

    """
    def __init__(self, metadata, call_url, call_data):
        """
        Args:
            metadata (dict): The raw API response to construct the class.
            call_url (str): The url used to call the API.
            call_data (AsyncYoutubeAPI): call data used for fetch functions.

        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided.
        """
        super().__init__(metadata, call_url, call_data)
        try:
            self.file_details: dict = metadata["fileDetails"]
            self.processing_details: dict = metadata["processingDetails"]
            self.suggestions: dict = metadata["suggestions"]
            self.has_custom_thumbnail: bool = self.content_details["hasCustomThumbnail"]
            self.self_declared_made_for_kids: bool = self.status["selfDeclaredMadeForKids"]
            self.dislike_count: Optional[int] = self.statistics.get("dislikeCount")
            self.file_name: str = self.file_details["fileName"]
            self.file_size: int = self.file_details["fileSize"]
            self.file_type: str = self.file_details["fileType"]
            self.file_container: str = self.file_details["container"]
            if self.file_details.get("videoStreams") is None:
                self.video_streams: Optional[list[VideoStream]] = None
            else:
                self.video_streams: Optional[list[VideoStream]] = \
                    [VideoStream(video_data) for video_data in self.file_details["videoStreams"]]
            if self.file_details.get("audioStreams") is None:
                self.audio_streams: Optional[list[AudioStream]] = None
            else:
                self.audio_streams: Optional[list[AudioStream]] = \
                    [AudioStream(audio_data) for audio_data in self.file_details["audioStreams"]]
            self.file_duration = datetime.timedelta(milliseconds=self.file_details["durationMS"])
            self.file_bitrate: int = self.file_details.get("bitrateBps")
            if self.file_details.get("creationTime") is None:
                self.file_creation_time: Optional[datetime.datetime] = None
            else:
                self.file_creation_time: Optional[datetime.datetime] = \
                    isodate.parse_datetime(self.file_details["creationTime"])
            self.processing_status: Optional[str] = self.processing_details.get("processingStatus")
            if self.processing_details.get("processingProgress") is None:
                self.processing_progress: Optional[ProcessingProgress] = None
            else:
                self.processing_progress: Optional[ProcessingProgress] = \
                    ProcessingProgress(self.processing_details["processingProgress"])
            self.processing_failure_reason: Optional[str] = self.processing_details.get("processingFailureReason")
            self.file_details_availability: Optional[str] = self.processing_details.get("fileDetailsAvailability")
            self.processing_issues_availability: Optional[str] = \
                self.processing_details.get("processingIssuesAvailability")
            self.tag_suggestions_availability: Optional[str] = self.processing_details.get("tagSuggestionsAvailability")
            self.editor_suggestions_availability: Optional[str] = \
                self.processing_details.get("editorSuggestionsAvailability")
            self.thumbnails_availability: Optional[str] = self.processing_details.get("thumbnailsAvailability")
            self.processing_errors: Optional[list[str]] = self.suggestions.get("processingErrors")
            self.processing_warnings: Optional[list[str]] = self.suggestions.get("processingWarnings")
            self.processing_hints: Optional[list[str]] = self.suggestions.get("processingHints")
            if self.suggestions.get("tagSuggestions") is None:
                self.tag_suggestions: Optional[list[TagSuggestion]] = None
            else:
                self.tag_suggestions: Optional[list[TagSuggestion]] = \
                    [TagSuggestion(tag_suggestion) for tag_suggestion in self.suggestions.get("tagSuggestions")]
            self.editor_suggestions: Optional[str] = self.suggestions.get("editorSuggestions")
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)


class YoutubeChannel:
    """
    A class representing metadata from a YouTube channel.

    Attributes:
        metadata (dict): The raw API response used to construct this class.
        call_url (str): The url used to call the API. Intended use is for debugging purposes.
        branding_settings (dict): encapsulates information about the branding of the channel.
        content_details (dict): encapsulates information about the channel's content.
        content_owner_details (dict): encapsulates channel data that is visible only to the YouTube Partner that has
            linked the channel to their Content Manager.
        id (str): The ID that YouTube uses to uniquely identify the channel.
        url (str): The URL of the channel.
        raw_localisations (Optional[dict]): encapsulates translations of the channel's metadata.
        snippet (dict): contains basic details about the channel, such as its title, description, and thumbnail images.
        statistics (dict): encapsulates statistics for the channel.
        status (dict): encapsulates information about the privacy status of the channel.
        topic_details (Optional[dict]): encapsulates information about topics associated with the channel.
        title (str): The channel's title.
        description (Optional[str]): The channel's description. The property's value has a maximum length of 1000
            characters.
        custom_url (Optional[str]): The channel's custom URL.
        username (Optional[str]): Alias for :attr:`custom_url`.
        published_at (datetime.datetime): The date and time that the channel was created.
        created_at (datetime.datetime): Alias for :attr:`published_at`.
        thumbnails (YoutubeThumbnailMetadata): The thumbnail images associated with the channel.
        icon (YoutubeThumbnailMetadata): Alias of :attr:`thumbnails`.
        pfp (YoutubeThumbnailMetadata): Alias of :attr:`thumbnails`.
        avatar (YoutubeThumbnailMetadata): Alias of :attr:`thumbnails`.
        default_language (Optional[str]): The language of the text in the :class:`YoutubeChannelMetadata` class's
            :attr:`title` and :attr:`description` properties.
        localised (Optional[LocalName]): The localized title and description for the channel or title and description
            in the :attr:`default_language`.
        localized (Optional[LocalName]): Alias for :attr:`localised`.
        country (Optional[str]): The country with which the channel is associated.
        related_playlists (dict): The playlists associated with the channel, such as the channel's uploaded videos or
            liked videos.
        likes_id (Optional[str]): The ID of the playlist that contains the channel's liked videos.
        likes_url (Optional[str]): The URL of the playlist that contains the channel's liked videos.
        uploads_id (Optional[str]): The ID of the playlist that contains the channel's uploaded videos.
        uploads_url (Optional[str]): The URL of the playlist that contains the channel's uploaded videos.
        view_count (int): The number of times the channel has been viewed.
        subscriber_count (int): The number of subscribers that the channel has. This is rounded to 3 significant
            figures.
        hidden_subscriber_count (bool): Whether the channel's subscriber count is publicly visible.
        video_count (int): The number of public videos uploaded to the channel.
        topic_categories (Optional[list[str]]): A list of Wikipedia URLs that describe the channel's content.
        topic_ids (Optional[list[str]]): A list of topic IDs associated with the channel.
        visibility (PrivacyStatus): The channel's privacy status. Can be :attr:`PrivacyStatus.private`,
            :attr:`PrivacyStatus.public` or :attr:`PrivacyStatus.unlisted`.
        is_linked (bool): Whether the channel data identifies a user that is already linked to either a YouTube
            username or a Google+ account.
        long_upload_status (LongUploadsStatus): whether the channel is eligible to upload videos that are more than 15
            minutes long.
        made_for_kids (Optional[bool]): Whether the channel is designated as child-directed, and it contains the
            current "made for kids" status of the channel.
        self_declared_made_for_kids (Optional[bool]): Designates the channel as child-directed.
        keywords (Optional[list[str]]): Keywords associated with your channel.
        tracking_analytics_account_id (Optional[str]): The ID for a Google Analytics account used to track and measure
            traffic to the channel.
        moderate_comments (Optional[bool]): Determines whether user-submitted comments left on the channel page need to
            be approved by the channel owner to be publicly visible.
        unsubscribed_trailer_id (Optional[str]): The ID of the video that should play in the featured video module in
            the channel page's browse view for unsubscribed viewers.
        unsubscribed_trailer_url (Optional[str]): The URL of the video that should play in the featured video module in
            the channel page's browse view for unsubscribed viewers.
        banner_external (Optional[YoutubeBanner]): The banner image that YouTube uses to generate the various
            banner image sizes for a channel.
        content_owner (Optional[str]): The ID of the content owner linked to the channel.
        time_linked (Optional[datetime.datetime]): The date and time of when the channel was linked to the content
            owner.
        localisations (Optional[list[LocalName]]): Encapsulates translations of the channel's metadata.
        localizations (Optional[list[LocalName]]): Alias for :attr:`localisations`.
    """
    def __init__(self, metadata: dict, call_url: str, call_data):
        """
        Args:
            metadata (dict): The raw API response to construct the class.
            call_url (str): The url used to call the API.
            call_data (AsyncYoutubeAPI): call data used for fetch functions.

        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided.
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self._call_data = call_data
            self.branding_settings: dict = metadata["brandingSettings"]
            self.content_details: dict = metadata["contentDetails"]
            self.content_owner_details: dict = metadata["contentOwnerDetails"]
            self.id: str = metadata["id"]
            self.url = CHANNEL_URL.format(self.id)
            self.raw_localisations: Optional[dict] = metadata.get("localizations")
            self.snippet: dict = metadata["snippet"]
            self.statistics: dict = metadata["statistics"]
            self.status: dict = metadata["status"]
            self.topic_details: Optional[dict] = metadata.get("topicDetails")
            self.title: str = self.snippet['title']
            self.description: Optional[str] = self.snippet.get("description")
            self.custom_url: Optional[str] = self.snippet.get("customUrl")
            self.username: Optional[str] = self.custom_url
            self.published_at = isodate.parse_datetime(self.snippet["publishedAt"])
            self.created_at = self.published_at
            self.thumbnails = YoutubeThumbnailMetadata(self.snippet["thumbnails"], self._call_data)
            self.icon = self.thumbnails
            self.pfp = self.thumbnails
            self.avatar = self.thumbnails
            self.default_language: Optional[str] = self.snippet.get("defaultLanguage")
            if self.snippet.get("localized") is None:
                self.localised: Optional[LocalName] = None
            else:
                self.snippet["localized"]["language"] = self.default_language
                self.localised: Optional[LocalName] = LocalName(**self.snippet["localized"])
            self.localized = self.localised
            self.country: Optional[str] = self.snippet.get("country")
            self.related_playlists: dict = self.content_details["relatedPlaylists"]
            self.likes_id: Optional[str] = self.related_playlists.get("likes")
            self.likes_url = PLAYLIST_URL.format(self.likes_id) if self.likes_id else None
            self.uploads_id: Optional[str] = self.related_playlists.get("uploads")
            self.uploads_url = PLAYLIST_URL.format(self.uploads_id) if self.uploads_id else None
            self.view_count: int = self.statistics["viewCount"]
            self.subscriber_count: int = self.statistics["subscriberCount"]
            self.hidden_subscriber_count: bool = self.statistics["hiddenSubscriberCount"]
            self.video_count: int = self.statistics["videoCount"]
            if self.topic_details is None:
                self.topic_categories: Optional[list[str]] = None
                self.topic_ids: Optional[list[str]] = None
            else:
                self.topic_categories: Optional[list[str]] = self.topic_details.get("topicCategories")
                self.topic_ids: Optional[list[str]] = self.topic_details.get("topicIds")
            self.visibility: Optional[PrivacyStatus] = PrivacyStatus(camel_to_snake(self.status["privacyStatus"]))
            self.is_linked: bool = self.status["isLinked"]
            self.long_upload_status = LongUploadsStatus(camel_to_snake(self.status["longUploadsStatus"]))
            self.made_for_kids: Optional[bool] = self.status.get("madeForKids")
            self.self_declared_made_for_kids: Optional[bool] = self.status.get("selfDeclaredMadeForKids")
            self._branding_channel = self.branding_settings["channel"]
            self.keywords: Optional[list[str]] = shlex.split(self._branding_channel["keywords"]) \
                if self._branding_channel.get("keywords") else None
            self.tracking_analytics_account_id: Optional[str] = self._branding_channel.get("trackingAnalyticsAccountId")
            self.moderate_comments: Optional[bool] = self._branding_channel.get("moderateComments")
            self.unsubscribed_trailer_id: Optional[str] = self._branding_channel.get("unsubscribedTrailer")
            self.unsubscribed_trailer_url: Optional[str] = VIDEO_URL.format(self.unsubscribed_trailer_id) \
                if self.unsubscribed_trailer_id else None
            self.banner_external = YoutubeBanner(
                self.branding_settings.get("image").get("bannerExternalUrl"), self._call_data
            ) if self.branding_settings.get("image") else None
            self.content_owner: Optional[str] = self.content_owner_details.get("contentOwner")
            self.time_linked = None if self.content_owner_details.get("timeLinked") is None else \
                isodate.parse_datetime(self.content_owner_details.get("timeLinked"))
            if self.raw_localisations is None:
                self.localisations: Optional[list[LocalName]] = None
            else:
                self.localisations: Optional[list[LocalName]] = []
                for localisation_name, localisation_value in self.raw_localisations.items():
                    self.localisations.append(LocalName(**localisation_value, language=localisation_name))
            self.localizations = self.localisations
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)

    async def fetch_uploads(self) -> Optional[list[PlaylistItem]]:
        """Fetches the playlist containing all public uploads associated with the channel.

        This ia an api call which then returns a
        :class:`PlaylistItem` object.

        Returns:
            Optional[list[PlaylistItem]]: A list containing playlist video objects of the channel's public uploads.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        if self.uploads_id:
            from .api import AsyncYoutubeAPI
            self._call_data: AsyncYoutubeAPI
            return await self._call_data.fetch_playlist_items(self.uploads_id)

    async def fetch_likes(self) -> Optional[list[PlaylistItem]]:
        """Fetches the playlist containing all videos the channel has liked if public.

        This ia an api call which then returns a
        :class:`PlaylistItem` object if public, otherwise ``None``.

        Returns:
            Optional[list[PlaylistItem]]: A list containing playlist video objects of the channel's public likes.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        if self.likes_id:
            from .api import AsyncYoutubeAPI
            self._call_data: AsyncYoutubeAPI
            return await self._call_data.fetch_playlist_items(self.likes_id)

    async def fetch_unsubscribed_trailer(self) -> Optional[YoutubeVideo]:
        """Fetches the channel trailer video if any.

        This ia an api call which then returns a
        :class:`YoutubeVideo` object if the channel has a trailer, otherwise ``None``.

        Returns:
            Optional[YoutubeVideo]: The video object containing data of the channel trailer.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        if self.unsubscribed_trailer_id:
            from .api import AsyncYoutubeAPI
            self._call_data: AsyncYoutubeAPI
            return await self._call_data.fetch_video(self.unsubscribed_trailer_id)

    async def fetch_comments(self, max_comments: Optional[int] = 50):
        """Fetches a list of related to the channel.

        This ia an api call which then returns a
        :class:`list[YoutubeCommentThread]` object.

        Returns:
            list[YoutubeCommentThread]: A list of comments related to the channel.

        Raises:
            HTTPException: Fetching the metadata failed.
            ChannelNotFound: The channel does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_channel_comments(self.id, max_comments)


REFERENCE_TABLE = {
    "video": [VIDEO_URL, YoutubeVideo],
    "channel": [CHANNEL_URL, YoutubeChannel],
    "playlist": [PLAYLIST_URL, YoutubePlaylist]
}


class YoutubeComment:
    """Represents information on an individual YouTube command.

    Information about the video the comment belongs to will not be available unless this object was access under
    :attr:`YoutubeCommentThread.replies`

    Attributes:
        metadata (dict): The raw API response used to construct this class.
        call_url (str): The url used to call the API. Intended use is for debugging purposes.
        snippet (dict): The raw snippet data used to construct part this class.
        id (str): The ID of the comment.
        author_display_name (str): The display name of the author (this is not their handle).
        author_profile_image_url (str): The image URL of the author's pfp.
        author_channel_id (Optional[str]): The ID of the author's channel.
        author_channel_url (Optional[str]): The URL of the author's channel.
        channel_id (Optional[str]): The id of the channel that the video belongs to.
        channel_url (Optional[str]): The url of the channel that the video belongs to.
        video_id (Optional[str]): The ID of the video that the comments refer to.
            Will be ``None`` unless part of a :class:`YoutubeCommentThread`.
        video_url (Optional[str]): The URL of the video that the comments refer to.
            Will be ``None`` unless part of a :class:`YoutubeCommentThread`.
        highlight_url (Optional[str]): The highlight URL of the comment.
            Will be ``None`` unless part of a :class:`YoutubeCommentThread`.
        url (Optional[str]): Alias of :attr:`highlight_url`
        text_display (str): The comment's text in either plain text or HTML.
        text_original (Optional[str]): The comment's raw text.
        parent_id (Optional[str]): The unique ID of the parent comment.
        can_rate (bool): whether the current viewer can rate the comment.
        viewer_rating (Optional[str]): The rating the viewer has given to this comment.
        like_count (int): The total number of likes on the comment.
        moderation_status (Optional[str]): The comment's moderation status.
        published_at (datetime.datetime): The date and time when the comment was originally published.
        updated_at (datetime.datetime): The date and time when the comment was last updated.
    """
    def __init__(self, metadata: dict, call_url: str, call_data):
        """
        Args:
            metadata (dict): The raw API response to construct the class.
            call_url (str): The url used to call the API.
            call_data (AsyncYoutubeAPI): call data used for fetch functions.

        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided.
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self._call_data = call_data
            self.snippet: dict = self.metadata['snippet']
            self.id: str = self.metadata['id']
            self.author_display_name: str = self.snippet['authorDisplayName']
            self.author_profile_image_url: str = self.snippet['authorProfileImageUrl']
            self.author_channel_url: Optional[str] = self.snippet.get("authorChannelUrl")
            self.author_channel_id: Optional[str] = self.snippet["authorChannelId"]['value'] \
                if self.snippet.get("authorChannelId") is not None else None
            self.channel_id: Optional[str] = self.snippet.get('channelId')
            self.channel_url: Optional[str] = CHANNEL_URL.format(self.channel_id) if self.channel_id else None
            self.video_id: Optional[str] = self.snippet.get('videoId')
            self.video_url: Optional[str] = VIDEO_URL.format(self.video_id) if self.video_id else None
            self.highlight_url: Optional[str] = HIGHLIGHT_URL.format(self.video_url, self.id) \
                if self.video_url else None
            self.url = self.highlight_url
            self.text_display: str = self.snippet['textDisplay']
            self.text_original: Optional[str] = self.snippet.get('textOriginal')
            self.parent_id: Optional[str] = self.snippet.get('parentId')
            self.can_rate: bool = self.snippet['canRate']
            self.viewer_rating: Optional[str] = self.snippet.get('viewerRating')
            self.like_count: int = self.snippet['likeCount']
            self.moderation_status: Optional[str] = self.snippet.get('moderationStatus')
            self.published_at = isodate.parse_datetime(self.snippet['publishedAt'])
            self.updated_at = isodate.parse_datetime(self.snippet['publishedAt'])
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)

    async def fetch_replies(self, max_comments: Optional[int] = 50):
        """Fetches a list of replies on the comment.

        This ia an api call which then returns a
        :class:`list[YoutubeComment]` object.

        Returns:
            list[YoutubeComment]: A list of replies on the comment.

        Raises:
            HTTPException: Fetching the metadata failed.
            CommentNotFound: The comment does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a comment id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        return await self._call_data.fetch_comment_replies(self.id, max_comments)


class YoutubeCommentThread:
    """Represents the structure of a comment (thread).

    Attributes:
        metadata (dict): The raw API response used to construct this class.
        call_url (str): The url used to call the API. Intended use is for debugging purposes.
        snippet (dict): The raw snippet data used to construct part this class.
        id (str): The ID of the comment.
        channel_id (Optional[str]): The id of the channel that the video belongs to.
        channel_url (Optional[str]): The url of the channel that the video belongs to.
        video_id (Optional[str]): The ID of the video that the comments refer to.
        video_url (Optional[str]): The URL of the video that the comments refer to.
        highlight_url (Optional[str]): The highlight URL of the comment.
        url (Optional[str]): Alias of :attr:`highlight_url`
        top_level_comment (YoutubeComment): The thread's top-level comment.
        can_reply (bool): Whether the current viewer can reply to the thread.
        total_reply_count (Optional[int]): The total number of replies that have been submitted in response to
            the top-level comment.
        is_public (bool): Whether the thread, including all of its comments and comment replies, is visible to all
            YouTube users.
        replies (Optional[list[YoutubeComment]]): The replies on the comment if any.
    """
    def __init__(self, metadata: dict, call_url: str, call_data):
        """
        Args:
            metadata (dict): The raw API response to construct the class.
            call_url (str): The url used to call the API.
            call_data (AsyncYoutubeAPI): call data used for fetch functions.

        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided.
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self._call_data = call_data
            self.snippet: dict = self.metadata['snippet']
            self.id: str = self.metadata['id']
            self.channel_id: Optional[str] = self.snippet.get('channelId')
            self.channel_url: Optional[str] = CHANNEL_URL.format(self.channel_id) if self.channel_id else None
            self.video_id: Optional[str] = self.snippet.get('videoId')
            self.video_url: Optional[str] = VIDEO_URL.format(self.video_id) if self.video_id else None
            self.highlight_url: Optional[str] = HIGHLIGHT_URL.format(self.video_url, self.id) \
                if self.video_url else None
            self.url = self.highlight_url
            self.top_level_comment = YoutubeComment(self.snippet['topLevelComment'], self.call_url, self._call_data)
            self.can_reply: bool = self.snippet['canReply']
            self.total_reply_count: Optional[int] = self.snippet.get('totalReplyCount')
            self.is_public: bool = self.snippet['isPublic']
            self.replies = [YoutubeComment(comment, self.call_url, self._call_data)
                            for comment in self.metadata['replies']['comments']] \
                if self.metadata.get('replies') is not None else None
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)


class YoutubeSearchResult:
    """Represents individual results from an API search.

    Attributes:
        data (dict): The raw API response used to construct this class.
        call_url (str): The url used to call the API. Intended use is for debugging purposes.
        kind_id (str): The raw kind of the result separated by a #. Could be video, channel or playlist.
        kind (type[Union[YoutubeVideo, YoutubeChannel, YoutubePlaylist]]).
        id (str): The ID of the object in the result.
        url (str): The URL of the object in the result.
        snippet (dict): The raw snippet data used to construct part this class.
        title (str): The title of the object in the search result.
        description (str): The description of the object in the search result.
        thumbnails (YoutubeThumbnailMetadata): The available thumbnails the object has.
        channel_title (Optional[str]): The title of the channel that published the resource that the search result
            identifies.
        live_broadcast_content: (LiveBroadcastContent): Indicates if the object is a livestream and if it is live.
    """
    def __init__(self, data: dict, call_url: str, call_data):
        """
            Args:
                data (dict): The raw API response to construct the class.
                call_url (str): The url used to call the API.
                call_data (AsyncYoutubeAPI): Call data used for fetch functions.

            Raises:
                MissingDataFromMetaData: There is malformed data in the metadata provided.
        """
        try:
            self.data = data
            self.call_url = call_url
            self._call_data = call_data
            self.kind_id: str = data["id"]["kind"]
            self._str_kind: str = self.kind_id.split('#')[1]
            self.kind: type[Union[YoutubeVideo, YoutubeChannel, YoutubePlaylist]] = REFERENCE_TABLE[self._str_kind][1]
            self.id = self.data["id"][f"{self._str_kind}Id"]
            self.url = REFERENCE_TABLE[self._str_kind][0].format(self.id)
            self.snippet = self.data["snippet"]
            self.title: str = self.snippet["title"]
            self.description: str = self.snippet["description"]
            self.thumbnails = YoutubeThumbnailMetadata(self.snippet["thumbnails"], self._call_data)
            self.channel_title: Optional[str] = self.snippet.get("channelTitle")
            self.live_broadcast_content: LiveBroadcastContent = \
                LiveBroadcastContent(self.snippet["liveBroadcastContent"])
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), data, missing_snippet_data)

    async def expand(self) -> Union[YoutubeVideo, YoutubeChannel, YoutubePlaylist]:
        """Expand the search result into its appropriate type.

        Returns:
            Union[YoutubeVideo, YoutubeChannel, YoutubePlaylist]: The proper object of the search result.

        Raises:
            HTTPException: Fetching the metadata failed.
            ResourceNotFound: The object does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a YouTube ID.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        from .api import AsyncYoutubeAPI
        self._call_data: AsyncYoutubeAPI
        fetch_item = getattr(self._call_data, f"fetch_{self._str_kind}")
        return await fetch_item(self.id)


class VideoCaption:
    """Represents data of an individual caption track on a video.

    Attributes:
        id (str): The ID of the caption track.
        snippet (dict): The raw snippet data used to construct part this class.
        video_id (str): The ID of the video that the caption track refer to.
        last_updated (datetime.datetime): The date and time when the caption track was last updated.
        track_kind (CaptionTrackKind): The caption track's type.
        language (str): The language of the caption track. The value is a BCP-47 language code.
        name (str): The name of the caption track. The name is intended to be visible to the user as an option during
            playback.
        audio_track_type (AudioTrackType): The type of audio track associated with the caption track.
        is_cc (bool): Whether the track contains closed captions. Defaults to ``False``.
        is_large (bool): Whether the caption track uses large text for the vision-impaired. Defaults to ``False``.
        is_easy_reader (bool): Whether the caption track is formatted for "easy reader," meaning it is at a third-grade
            level for language learners. Defaults to ``False``.
        is_auto_synced (bool): Whether YouTube synchronized the caption track to the audio track in the video.
        status (CaptionStatus): The caption track's status.
        failure_reason (CaptionFailureReason): The reason that YouTube failed to process the caption track.
    """
    def __init__(self, metadata: dict, call_url: str, call_data):
        """
            Args:
                metadata (dict): The raw API response to construct the class.
                call_url (str): The url used to call the API.
                call_data (AsyncYoutubeAPI): Call data used for fetch functions.

            Raises:
                MissingDataFromMetaData: There is malformed data in the metadata provided.
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self._call_data = call_data
            self.id: str = self.metadata["id"]
            self.snippet: dict = self.metadata["snippet"]
            self.video_id: str = self.snippet["videoId"]
            self.last_updated = isodate.parse_datetime(self.snippet["lastUpdated"])
            self.track_kind = CaptionTrackKind(self.snippet["trackKind"].lower())
            self.language: str = self.snippet.get("language")
            self.name: str = self.snippet.get("name")
            self.audio_track_type = AudioTrackType(self.snippet["audioTrackType"])
            self.is_cc: bool = self.snippet["isCC"]
            self.is_large: bool = self.snippet["isLarge"]
            self.is_easy_reader: bool = self.snippet["isEasyReader"]
            self.is_draft: bool = self.snippet["isDraft"]
            self.is_auto_synced: bool = self.snippet["isAutoSynced"]
            self.status = CaptionStatus(self.snippet["status"]) if self.snippet.get("status") else None
            self.failure_reason = CaptionFailureReason(camel_to_snake(self.snippet["failureReason"])) \
                if self.snippet.get("failureReason") else None
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)
