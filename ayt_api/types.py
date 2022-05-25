import datetime
from typing import Union

import isodate
from .exceptions import MissingDataFromMetadata


class YoutubeThumbnail:
    """Data for an individual YouTube thumbnail.
    Attributes:
        data (dict): The raw thumbnail data
        url (str): The file url for the thumbnail
        width (int): The amount of horizontal pixels in the thumbnail
        height (int): The amount of vertical pixels in the thumbnail
        resolution (str): The WIDTHxHeight of the thumbnail
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw thumbnail data
        """
        self.data = data
        self.url: str = data.get("url")
        self.width: int = data.get("width")
        self.height: int = data.get("height")
        self.resolution = "{}x{}".format(self.width, self.height)


class YoutubeThumbnailMetadata:
    """Data for the available thumbnails of a video"""
    def __init__(self, thumbnail_metadata: dict):
        """
        Args:
            thumbnail_metadata (dict): the raw thumbnail metadata to provide
        """
        self.metadata = thumbnail_metadata

    @property
    def default(self):
        """The default video thumbnail. Could be None.
        Returns:
            YoutubeThumbnail: A YouTube thumbnail object. Could be None"""
        if self.metadata.get("default") is not None:
            return YoutubeThumbnail(self.metadata["default"])

    @property
    def medium(self):
        """The medium video thumbnail. Could be None
        Returns:
            YoutubeThumbnail: A YouTube thumbnail object. Could be None"""
        if self.metadata.get("medium") is not None:
            return YoutubeThumbnail(self.metadata["medium"])

    @property
    def high(self):
        """The high video thumbnail. Could be None
        Returns:
            YoutubeThumbnail: A YouTube thumbnail object. Could be None"""
        if self.metadata.get("high") is not None:
            return YoutubeThumbnail(self.metadata["high"])

    @property
    def standard(self):
        """The standard video thumbnail. Could be None
        Returns:
            YoutubeThumbnail: A YouTube thumbnail object. Could be None"""
        if self.metadata.get("standard") is not None:
            return YoutubeThumbnail(self.metadata["standard"])

    @property
    def maxres(self):
        """The maximum resolution video thumbnail. Could be None
        Returns:
            YoutubeThumbnail: A YouTube thumbnail object. Could be None"""
        if self.metadata.get("maxres") is not None:
            return YoutubeThumbnail(self.metadata["maxres"])


class LocalName:
    """Represents the video title and description in a local language if available
    Attributes:
        data (dict): The raw data associated with the local text
        language (str): The language code
        title (str): The title in a local language
        description (str): The description in a local language
    """
    def __init__(self, data: dict, lang_key: str = None):
        """
        Args:
            data (dict): The raw local text data
            lang_key (str): The language code
        """
        self.data = data
        self.language = lang_key
        self.title: str = data.get("title")
        self.description: str = data.get("description")


class RegionRestrictions:
    """Represents information about the countries where a video is (or is not) viewable.
    Attributes:
        data (dict): The raw data about what regions are blocked or allowed

        allowed (list[str]): The countries that are allowed to view the video. Could be None

        blocked (list[str]): The countries that are blocked from viewing the video. Could be None"""
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw regionRestriction data
        """
        self.data = data
        self.allowed: list[str] = self.data.get("allowed")
        self.blocked: list[str] = self.data.get("blocked")


class ContentRating:
    """Specifies the ratings that the video received under various rating schemes.

        There are many attributes for each rating system, only 1 or 2 (if there is a reason) will be available,
        the rest will be None or all if there is no restrictions set.
    Attributes:
        acb (str): The video's Australian Classification Board (ACB) or Australian Communications and Media Authority
            (ACMA) rating. ACMA ratings are used to classify children's television programming.
        youtube (str): A rating that YouTube uses to identify age-restricted content.
    """
    def __init__(self, data: dict):
        """

        :param data:
        """
        self.acb: str = data.get("acbRating")
        self.agcom: str = data.get("agcomRating")
        self.anatel: str = data.get("anatelRating")
        self.bbfc: str = data.get("bbfcRatingRating")
        self.bfvc: str = data.get("bfvcRatingRating")
        self.bmukk: str = data.get("bmukkRatingRating")
        self.catv: str = data.get("catvRatingRating")
        self.catvfr: str = data.get("catvfrRatingRating")
        self.cbfc: str = data.get("cbfcRatingRating")
        self.ccc: str = data.get("cccRatingRating")
        self.cce: str = data.get("cceRatingRating")
        self.chfilm: str = data.get("chfilmRatingRating")
        self.chvrs: str = data.get("chvrsRatingRating")
        self.cicf: str = data.get("cicfRatingRating")
        self.cna: str = data.get("cnaRatingRating")
        self.cnc: str = data.get("cncRatingRating")
        self.csa: str = data.get("csaRatingRating")
        self.cscf: str = data.get("cscfRatingRating")
        self.czfilm: str = data.get("czfilmRatingRating")
        self.djctq: str = data.get("djctqRatingRating")
        self.djctq_rating_reasons: list[str] = data.get("djctqRatingReasons")
        self.ecbmct: str = data.get("ecbmctRating")
        self.eefilm: str = data.get("eefilmRating")
        self.egfilm: str = data.get("egfilmRating")
        self.eirin: str = data.get("eirinRating")
        self.fcbm: str = data.get("fcbmRating")
        self.fco: str = data.get("fcoRating")
        self.fpb: str = data.get("fpbRating")
        self.fpb_rating_reasons: list[str] = data.get("fpbRatingReasons")
        self.fsk: str = data.get("fskRating")
        self.grfilm: str = data.get("grfilmRating")
        self.icaa: str = data.get("icaaRating")
        self.ifco: str = data.get("ifcoRating")
        self.ilfilm: str = data.get("ilfilmRating")
        self.incaa: str = data.get("incaaRating")
        self.kfcb: str = data.get("kfcbRating")
        self.kijkwijzer: str = data.get("kijkwijzerRating")
        self.kmrb: str = data.get("kmrbRating")
        self.lsf: str = data.get("lsfRating")
        self.mccaa: str = data.get("mccaaRating")
        self.mccyp: str = data.get("mccypRating")
        self.mcst: str = data.get("mcstRating")
        self.mda: str = data.get("mdaRating")
        self.medietilsynet: str = data.get("medietilsynetRating")
        self.meku: str = data.get("mekuRatingRating")
        self.mibac: str = data.get("mibacRating")
        self.moc: str = data.get("mocRating")
        self.moctw: str = data.get("moctwRating")
        self.mpaa: str = data.get("mpaaRating")
        self.mpaat: str = data.get("mpaatRating")
        self.mtrcb: str = data.get("mtrcbRating")
        self.nbc: str = data.get("nbcRating")
        self.nfrc: str = data.get("nfrcRating")
        self.nfvcb: str = data.get("nfvcbRating")
        self.nkclv: str = data.get("nkclvRating")
        self.oflc: str = data.get("oflcRating")
        self.pefilm: str = data.get("pefilmRating")
        self.resorteviolencia: str = data.get("resorteviolenciaRating")
        self.rtc: str = data.get("rtcRating")
        self.rte: str = data.get("rteRating")
        self.russia: str = data.get("russiaRating")
        self.skfilm: str = data.get("skfilmRating")
        self.smais: str = data.get("smaisRating")
        self.smsa: str = data.get("smsaRating")
        self.tvpg: str = data.get("tvpgRating")
        self.youtube: str = data.get("ytRating")


class RecordingLocation:
    """The geolocation information associated with the video. if specified by the video uploader
    Attributes:
        data (dict): The raw geolocation data used to construct this class
        latitude (float): Latitude in degrees.
        longitude (float): Longitude in degrees.
        altitude (float): Altitude above the reference ellipsoid, in meters.
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw geolocation data
        """
        self.data = data
        self.latitude: float = self.data.get("latitude")
        self.longitude: float = self.data.get("longitude")
        self.altitude: float = self.data.get("altitude")


class RecordingDetails:
    """Contains details of the location and date of the video recording if specified by the video uploader.
    Attributes:
        data (dict): The raw information about the location, date and address where the video was recorded.
        description (str): The text description of the location where the video was recorded.
        location (RecordingLocation): The geolocation information associated with the video.
        date (datetime.datetime): The date and time when the video was recorded.
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw recording details used to construct this class
        """
        self.data = data
        self.description: str = data.get("locationDescription")
        if data.get("location") is None:
            self.location = None
        else:
            self.location = RecordingLocation(data["location"])
        if data.get("recordingDate") is None:
            self.date = None
        else:
            self.date = isodate.parse_datetime(data["recordingDate"])


class VideoStream:
    """Metadata about a video stream for a youtube video
    Attributes:
        data (dict): The raw video stream data used to construct this class
        width (int): The encoded video content's width in pixels.
        height (int): The encoded video content's height in pixels.
        resolution (str): width x height
        frame_rate (float): The video stream's frame rate, in frames per second.
        aspect_ratio (float): The video content's display aspect ratio
        codec (string): The video codec that the stream uses.
        bitrate (int): The video stream's bitrate, in bits per second.
        rotation (string):
            The amount that YouTube needs to rotate the original source content to properly display the video.
        vendor (string):
            A value that uniquely identifies a video vendor. Typically, the value is a four-letter vendor code.
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw video stream data
        """
        self.data = data
        self.width: int = data.get("widthPixels")
        self.height: int = data.get("heightPixels")
        self.resolution: str = '{}x{}'.format(self.width, self.height)
        self.frame_rate: float = data.get("frameRateFps")
        self.aspect_ratio: float = data.get("aspectRatio")
        self.codec: str = data.get("codec")
        self.bitrate: int = data.get("bitrateBps")
        self.rotation: str = data.get("rotation")
        self.vendor: str = data.get("vendor")


class AudioStream:
    """Metadata about an audio stream for a youtube video
    Attributes:
        data (dict): The raw audio stream data used to construct this class
        channel_count (int): The number of audio channels that the stream contains.
        codec (string): The audio codec that the stream uses.
        bitrate (int): The audio stream's bitrate, in bits per second.
        vendor (string):
            A value that uniquely identifies a video vendor. Typically, the value is a four-letter vendor code.

    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw audio stream data
        """
        self.data = data
        self.channel_count: int = data.get("channelCount")
        self.codec: str = data.get("codec")
        self.bitrate: int = data.get("bitrateBps")
        self.vendor: str = data.get("vendor")


class ProcessingProgress:
    """Contains information about the progress YouTube has made in processing the video.
    Attributes:
        data (dict): The raw processing progress data used to construct this class
        parts_total (int): An estimate of the total number of parts that need to be processed for the video.
        parts_processed (int): The number of parts of the video that YouTube has already processed.
        time_left (datetime.timedelta):
            An estimate of the amount of time, in milliseconds, that YouTube needs to finish processing the video.
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): Raw processing progress
        """
        self.data = data
        self.parts_total: int = data.get("partsTotal")
        self.parts_processed: int = data.get("partsProcessed")
        if data.get('timeLeftMs') is None:
            self.time_left = None
        else:
            self.time_left = datetime.timedelta(milliseconds=data["timeLeftMs"])


class TagSuggestion:
    """
    A list of keyword tags that could be added to the video's metadata to increase the likelihood that users will
        locate your video when searching or browsing on YouTube.
    Attributes:
        data (dict): The raw tag suggestions data used to construct this class
        tag (str): The keyword tag suggested for the video.
        category_restricts (list[str]): A set of video categories for which the tag is relevant.
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw tag suggestions data
        """
        self.data = data
        self.tag: str = data.get("tag")
        self.category_restricts: list[str] = data.get("categoryRestricts")


class YoutubePlaylistMetadata:
    """Data class for YouTube playlists
    Attributes:
        metadata (dict): The raw API response used to construct this class
        call_url (str): The url used to call the API. Intended use is for debugging purposes
        id (str): The ID of the playlist. Example: "PLwZcI0zn-Jhemx2m_gpYqQfnc3l4xA4fp" from the url:
            "https://www.youtube.com/playlist?list=PLwZcI0zn-Jhemx2m_gpYqQfnc3l4xA4fp"
        url (str): The URL of the playlist
        snippet (dict): The raw snippet data used to construct this class
        status (dict): The raw status data used to construct part of this class
        content_details (dict): The raw content details data used to construct part of this class
        player (dict): The raw player data used to construct part of this class
        raw_localisations (dict): The raw localisation data used to construct part of this class
        published_at (datetime.datetime): The date and time the playlist was published
        channel_id (str): The id of the channel that created the playlist
        channel_url (str): The url of the channel that created the playlist
        title (str): The title of the playlist
        description (str): The description of the playlist
        thumbnails (YoutubeThumbnailMetadata): The available thumbnails the playlist has
        channel_title: (str) The name of the channel that created the playlist
        default_language (str): The default language the video is set in. Can be None
        localised (LocalName): The localised language of the title and description of the video
        localized (LocalName): an alias of localised
        visibility (str): The video's privacy status. Can be private, public or unlisted
        item_count (int): The number of items in the playlist
        embed_html (str): An <iframe> tag that embeds a player that plays the video.
        localisations (list[LocalName]): contains translations of the video's metadata.
        localizations (list[LocalName]): an alias of localisations
    """
    def __init__(self, metadata: dict, call_url: str):
        """
        Args:
            metadata (dict): The raw API response to provide
            call_url (str): The url used to call the API. Intended use is for debugging purposes
        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self.id: str = metadata["id"]
            self.url: str = f'https://www.youtube.com/playlist?list={self.id}'
            self.snippet: dict = metadata["snippet"]
            self.status: dict = metadata["status"]
            self.content_details: dict = metadata["contentDetails"]
            self.player: dict = metadata["player"]
            self.raw_localisations: dict = metadata.get("localizations")
            if self.snippet.get("publishedAt") is None:
                self.published_at = None
            else:
                self.published_at = isodate.parse_datetime(self.snippet["publishedAt"])
            self.channel_id: str = self.snippet.get("channelId")
            if self.channel_id is None:
                self.channel_url = None
            else:
                self.channel_url: str = f'https://www.youtube".com/channel/{self.channel_id}'
            self.title: str = self.snippet.get("title")
            self.description: str = self.snippet.get("description")
            self.thumbnails = YoutubeThumbnailMetadata(self.snippet.get("thumbnails"))
            self.channel_title: str = self.snippet.get("channelTitle")
            self.default_language: str = self.snippet.get("defaultLanguage")
            if self.snippet.get("localized") is None:
                self.localized = None
                self.localised = None
            else:
                self.localised = LocalName(self.snippet["localized"])
                self.localized = self.localised
            self.visibility: str = self.status.get("privacyStatus")
            self.item_count: int = self.content_details.get("itemCount")
            self.embed_html: str = self.player.get("embedHtml")
            if self.raw_localisations is None:
                self.localisations = None
            else:
                self.localisations: list[LocalName] = []
                for localisation_name, localisation_value in self.raw_localisations.items():
                    self.localisations.append(LocalName(localisation_value, localisation_name))
            self.localizations = self.localisations
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)


class ABCVideoMetadata:
    pass


class PlaylistVideoMetadata(ABCVideoMetadata):
    """A data class for videos in a playlist
    Attributes:
        metadata (dict): The raw metadata from the API call used to construct this class
        call_url (str): The url used to call the API. Intended use is for debugging purposes
        id (str): The ID of the video in the playlist. Example: "dQw4w9WgXcQ" from the url:
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ". Look familiar?
        position (int): The position in the playlist the video is in
        url (str): The URL of the video
        title (str): The title of the video
        description (str): The description of the video
        added_at (datetime.datetime): The date and time the video was added to the playlist
        thumbnails (YoutubeThumbnailMetadata): The available thumbnails the video has
        channel_title: (str) The name of the channel that the video belongs to
        channel_id (str): The id of the channel that the video belongs to
        channel_url (str): The url of the channel that the video belongs to
        playlist_id (str): The ID of the playlist the video is in
        playlist_url (str): The URL of the playlist the video is in
        published_at (datetime.datetime): The date and time the video was published
        note (str): A user-generated note for this item.
        visibility (str): The playlist item's privacy status. Can be public, private or unlisted
    """
    def __init__(self, metadata: dict, call_url: str):
        """
        Args:
            metadata: The snippet metadata of the video in the playlist
            call_url (str): The url used to call the API. Intended use is for debugging purposes
        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self.snippet = metadata["snippet"]
            self.content_details = metadata["contentDetails"]
            self.status = metadata["status"]
            if self.snippet.get("publishedAt") is None:
                self.added_at = None
            else:
                self.added_at = isodate.parse_datetime(self.snippet["publishedAt"])
            self.position: int = self.snippet.get("position")
            self.id: str = self.content_details.get("videoId")
            self.url: str = f'https://www.youtube.com/watch?v={self.id}'
            self.title: str = self.snippet.get("title")
            self.description: str = self.snippet.get('description')
            self.thumbnails = YoutubeThumbnailMetadata(self.snippet["thumbnails"])
            self.channel_id: str = self.snippet.get("videoOwnerChannelId")
            if self.channel_id is None:
                self.channel_url = None
            else:
                self.channel_url: str = f'https://www.youtube".com/channel/{self.channel_id}'
            self.channel_title: str = self.snippet.get("videoOwnerChannelTitle")
            self.playlist_id = self.snippet.get("playlistId")
            self.playlist_url = f'https://www.youtube.com/playlist?list={self.playlist_id}'
            self.note = self.content_details.get("note")
            if self.content_details.get("videoPublishedAt") is None:
                self.published_at = None
            else:
                self.published_at = isodate.parse_datetime(self.content_details["videoPublishedAt"])
            self.visibility = self.status.get("privacyStatus")
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)


class YoutubeVideoMetadata(ABCVideoMetadata):
    """A data class containing video data such as the title, id, description, channel, etc.
        Attributes:
            metadata (dict): The raw API response used to construct this class
            call_url (str): The url used to call the API. Intended use is for debugging purposes
            id (str): The ID of the video. Example: "dQw4w9WgXcQ" from the url:
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ". Look familiar?
            snippet (dict): The raw snippet data used to construct part this class
            content_details (dict): The raw content details data used to construct part of this class
            status (dict): The raw status data used to construct part of this class
            statistics (dict): The raw statistics data used to construct part of this class
            player (dict): The raw player data used to construct part of this class
            topic_details (dict): The raw topic details used to construct part of this class
            raw_recording_details (dict): The raw recording details used to construct part of this class
            raw_localisations (dict): The raw localisation data used to construct part of this class
            url (str): The URL of the video
            title (str): The title of the video
            description (str): The description of the video
            published_at (datetime.datetime): The date and time the video was published
            thumbnails (YoutubeThumbnailMetadata): The available thumbnails the video has
            channel_title: (str) The name of the channel that the video belongs to
            channel_id (str): The id of the channel that the video belongs to
            channel_url (str): The url of the channel that the video belongs to.
            tags (list[str]): The tags the uploaded has provided to make the video appear in search results relating
                to it
            category_id (int): The id of the category that was set for the video
            live_broadcast_content: (str): Indicates if the video is a livestream and if it is live
            default_language (str): The default language the video is set in
            localised (LocalName): The localised language of the title and description of the video
            localized (LocalName): an alias of localised
            default_audio_language (str): The default audio language the video is set in
            duration (Union[isodate.Duration, datetime.timedelta, _NotImplementedType]): The length of the video
            dimension (str): Indicates whether the video is available in 3D or in 2D
            definition (str): Indicates whether the video is available in high definition (HD) or only in standard
                definition.
            has_captions (bool): Indicates whether captions are available for the video.
            licensed_content (bool): Indicates whether the video represents licensed content, which means that the
                content was uploaded to a channel linked to a YouTube content partner and then claimed by that partner.
            region_restrictions (RegionRestrictions): contains information about the countries where a video is
                (or is not) viewable. Can be None
            content_rating (ContentRating): Specifies the ratings that the video received under various rating schemes.
            age_restricted (bool): Whether the video is age restricted or not.
            projection (str): Specifies the projection format of the video. (example: 360 or rectangular)
            upload_status (str): The status of the uploaded video.
            failure_reason (str): Explains why a video failed to upload. This attribute is only present if
                the upload_status attribute is set to "failed".
            rejection_reason (str): Explains why YouTube rejected an uploaded video. This attribute is only
                present if the upload_status attribute is set to "failed".
            visibility (str): The video's privacy status. Can be private, public or unlisted
            publish_set_at (datetime.datetime): The date and time when the video is scheduled to publish if any.
            license (str): The video's license. valid values for this attribute is creativeCommon and youtube
            embeddable (bool): Indicates whether the video can be embedded on another website.
            public_stats_viewable (bool): Indicates whether the extended video statistics on the video's watch page are
                publicly viewable.
            made_for_kids (bool): Indicates whether the video is designated as child-directed, and it contains the
                current "made for kids" status of the video.
            view_count (int): The number of times the video has been viewed.
            like_count (int): The number of users who have indicated that they liked the video.
            embed_html (str): An <iframe> tag that embeds a player that plays the video.
            embed_height (str): The height of the embedded player returned to the embed_html attribute.
                Is None unless the height and aspect ratio is known
            embed_width (str): The width of the embedded player returned to the embed_html attribute.
                Is None unless the width and aspect ratio is known
            topic_categories (list[str]): A list of Wikipedia URLs that provide a high-level description of the
                video's content.
            recording_details (RecordingDetails): Encapsulates information about the location, date and address where
                the video was recorded.
            stream_actual_start_time (datetime.datetime): The time that the broadcast actually started.
            stream_scheduled_start_time (datetime.datetime): The time that the broadcast is scheduled to begin.
            stream_actual_end_time (datetime.datetime): The time that the broadcast actually ended.
            stream_scheduled_end_time (datetime.datetime): The time that the broadcast is scheduled to end.
            stream_concurrent_viewers (int): The number of viewers currently watching the broadcast.
            stream_active_live_chat_id (str): The ID of the currently active live chat attached to this video.
            localisations (list[LocalName]): contains translations of the video's metadata.
            localizations (list[LocalName]): an alias of localisations
        """
    def __init__(self, metadata: dict, call_url: str):
        """
        Args:
            metadata: The snippet metadata of the video in the playlist
            call_url (str): The url used to call the API. Intended use is for debugging purposes
        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided
        """
        try:
            self.metadata = metadata
            self.call_url = call_url
            self.snippet: dict = metadata["snippet"]
            self.content_details: dict = metadata["contentDetails"]
            self.status: dict = metadata["status"]
            self.statistics: dict = metadata["statistics"]
            self.player: dict = metadata["player"]
            self.topic_details: dict = metadata.get("topicDetails")
            self.raw_recording_details: dict = metadata["recordingDetails"]
            self.live_streaming_details: dict = metadata.get("liveStreamingDetails")
            self.raw_localisations: dict = metadata.get("localizations")
            self.id: str = metadata["id"]
            self.url: str = f'https://www.youtube.com/watch?v={self.id}'
            if self.snippet.get("publishedAt") is None:
                self.published_at = None
            else:
                self.published_at = isodate.parse_datetime(self.snippet["publishedAt"])
            self.channel_id: str = self.snippet.get("channelId")
            if self.channel_id is None:
                self.channel_url = None
            else:
                self.channel_url: str = f'https://www.youtube".com/channel/{self.channel_id}'
            self.title: str = self.snippet.get("title")
            self.description: str = self.snippet.get("description")
            self.thumbnails = YoutubeThumbnailMetadata(self.snippet.get("thumbnails"))
            self.channel_title: str = self.snippet.get("channelTitle")
            self.tags: list[str] = self.snippet.get("tags")
            self.category_id: int = int(self.snippet.get("categoryId"))
            self.live_broadcast_content: str = self.snippet.get("liveBroadcastContent")
            self.default_language: str = self.snippet.get("defaultLanguage")
            if self.snippet.get("localized") is None:
                self.localized = None
            else:
                self.localised = LocalName(self.snippet["localized"])
            self.localized = self.localised
            self.default_audio_language: str = self.snippet.get("defaultAudioLanguage")
            self.duration = isodate.parse_duration(self.content_details.get("duration"))
            self.dimension: str = self.content_details.get("dimension")
            self.definition: str = self.content_details.get("definition")
            if self.content_details.get("caption") == "true":
                self.has_captions = True
            elif self.content_details.get("caption") == "false":
                self.has_captions = False
            else:
                self.has_captions = None
            self.licensed_content: bool = self.content_details.get("licensedContent")
            if self.content_details.get("regionRestriction") is None:
                self.region_restrictions = None
            else:
                self.region_restrictions = RegionRestrictions(self.content_details["regionRestriction"])
            self.content_rating = ContentRating(self.content_details["contentRating"])
            self.age_restricted = bool(self.content_details["contentRating"].get("ytRating"))
            self.projection: str = self.content_details.get("projection")
            self.upload_status: str = self.status.get("uploadStatus")
            self.failure_reason: str = self.status.get("failureReason")
            self.rejection_reason: str = self.status.get("rejectionReason")
            self.visibility: str = self.status.get("privacyStatus")
            if self.status.get("publishAt") is None:
                self.publish_set_at = None
            else:
                self.publish_set_at = isodate.parse_datetime(self.status.get("publishAt"))
            self.license: str = self.status.get("license")
            self.embeddable: bool = self.status.get("embeddable")
            self.public_stats_viewable: bool = self.status.get("publicStatsViewable")
            self.made_for_kids: bool = self.status.get("madeForKids")
            self.view_count: int = self.statistics.get("viewCount")
            self.like_count: int = self.statistics.get("likeCount")
            self.comment_count: int = self.statistics.get("commentCount")
            self.embed_html: str = self.player.get("embedHtml")
            self.embed_height: str = self.player.get("embedHeight")
            self.embed_width: str = self.player.get("embedWidth")
            if self.topic_details is None:
                self.topic_categories = None
            else:
                self.topic_categories: list[str] = self.topic_details.get("topicCategories")
            self.recording_details = RecordingDetails(self.raw_recording_details)
            self.stream_actual_start_time = None
            self.stream_scheduled_start_time = None
            self.stream_actual_end_time = None
            self.stream_scheduled_end_time = None
            self.stream_concurrent_viewers = None
            self.stream_active_live_chat_id = None
            if self.live_streaming_details is None:
                pass
            else:
                if self.live_streaming_details.get("actualStartTime") is None:
                    pass
                else:
                    self.stream_actual_start_time = \
                        isodate.parse_datetime(self.live_streaming_details.get("actualStartTime"))
                if self.live_streaming_details.get("scheduledStartTime") is None:
                    pass
                else:
                    self.stream_scheduled_start_time = \
                        isodate.parse_datetime(self.live_streaming_details.get("scheduledStartTime"))
                if self.live_streaming_details.get("actualEndTime") is None:
                    pass
                else:
                    self.stream_actual_end_time = \
                        isodate.parse_datetime(self.live_streaming_details.get("actualEndTime"))
                if self.live_streaming_details.get("scheduledEndTime") is None:
                    pass
                else:
                    self.stream_scheduled_end_time = \
                        isodate.parse_datetime(self.live_streaming_details.get("scheduledEndTime"))
                self.stream_concurrent_viewers: int = self.live_streaming_details.get("concurrentViewers")
                self.stream_active_live_chat_id: str = self.live_streaming_details.get("activeLiveChatId")
            if self.duration.total_seconds() < 1 and self.stream_actual_start_time is not None:
                self.duration = \
                    datetime.timedelta(
                        seconds=datetime.datetime.now().timestamp() - self.stream_actual_start_time.timestamp())
            if self.raw_localisations is None:
                self.localisations = None
            else:
                self.localisations: list[LocalName] = []
                for localisation in self.raw_localisations.items():
                    self.localisations.append(LocalName(localisation[1], localisation[0]))
            self.localizations = self.localisations

        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)


class AuthorisedYoutubeVideoMetadata(YoutubeVideoMetadata):
    """
    A data class containing owner only information video data such as the file and processing information.

        THis class is used if authorisation is provided that you are the owner of the video. It contains
        attributes only accessible by the video owner as well as attributes inherited
        from :class:`YoutubeVideoMetadata`

    Attributes:
        file_details (dict): The raw file details used to construct this class
        has_custom_thumbnail (bool): Indicates whether the video uploader has provided a custom thumbnail image for
            the video.
        self_declared_made_for_kids (bool): This Attribute allows the channel owner to designate the video as being
                child-directed.
        dislike_count (int): The number of users who have indicated that they disliked the video.
        file_name (str): The uploaded file's name.
        file_size (int): The uploaded file's size in bytes.
        file_type (str): The uploaded file's type as detected by YouTube's video processing engine.
        file_container (str): The uploaded video file's container format.
        video_streams (list[VideoStream]): A list of video streams contained in the uploaded video file.
        audio_streams (list[AudioStream]): A list of audio streams contained in the uploaded video file.
        file_duration (datetime.timedelta): The length of the uploaded video millisecond accurate.
        file_bitrate (int): The uploaded video file's combined (video and audio) bitrate in bits per second.
        file_creation_time (datetime.datetime): The date and time when the uploaded video file was created.
        processing_status (str): The video's processing status.
        processing_progress (ProcessingProgress):
            contains information about the progress YouTube has made in processing the video
        processing_failure_reason (str): The reason that YouTube failed to process the video.
        file_details_availability (str): This value indicates whether file details are available for the uploaded video.
        processing_issues_availability (str):
            indicates whether the video processing engine has generated suggestions that might improve YouTube's
            ability to process the video, warnings that explain video processing problems, or errors that cause
            video processing problems.
        tag_suggestions_availability (str):
            This value indicates whether keyword (tag) suggestions are available for the video.
        editor_suggestions_availability (str):
            This value indicates whether video editing suggestions, which might improve video quality or the playback
            experience, are available for the video.
        thumbnails_availability (str): This value indicates whether thumbnail images have been generated for the video.
        processing_errors (list[str]):
            A list of errors that will prevent YouTube from successfully processing the uploaded video.
        processing_warnings (list[str]): A list of reasons why YouTube may have difficulty transcoding the uploaded
            video or that might result in an erroneous transcoding.
        processing_hints (list[str]): A list of suggestions that may improve YouTube's ability to process the video.
        tag_suggestions (list[TagSuggestion]):
            A list of keyword tags that could be added to the video's metadata to increase the likelihood that users
            will locate your video when searching or browsing on YouTube.
        editor_suggestions (list[str]):
            A list of video editing operations that might improve the video quality or playback experience of the
            uploaded video.

    """
    def __init__(self, metadata, call_url):
        """
        Args:
            metadata: The snippet metadata of the video in the playlist
            call_url (str): The url used to call the API. Intended use is for debugging purposes
        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided
        """
        super().__init__(metadata, call_url)
        try:
            self.file_details: dict = metadata["fileDetails"]
            self.processing_details: dict = metadata["processingDetails"]
            self.suggestions: dict = metadata["suggestions"]
            self.has_custom_thumbnail: bool = self.content_details.get("hasCustomThumbnail")
            self.self_declared_made_for_kids: bool = self.status.get("selfDeclaredMadeForKids")
            self.dislike_count: int = self.statistics.get("dislikeCount")
            self.file_name: str = self.file_details.get("fileName")
            self.file_size: int = self.file_details.get("fileSize")
            self.file_type: str = self.file_details.get("fileType")
            self.file_container: str = self.file_details.get("container")
            if self.file_details.get("videoStreams") is None:
                self.video_streams = None
            else:
                self.video_streams: list[VideoStream] = \
                    [VideoStream(video_data) for video_data in self.file_details["videoStreams"]]
            if self.file_details.get("audioStreams") is None:
                self.audio_streams = None
            else:
                self.audio_streams: list[AudioStream] = \
                    [AudioStream(audio_data) for audio_data in self.file_details["audioStreams"]]
            if self.file_details.get("durationMS") is None:
                self.file_duration = None
            else:
                self.file_duration = datetime.timedelta(milliseconds=self.file_details["durationMS"])
            self.file_bitrate: int = self.file_details.get("bitrateBps")
            if self.file_details.get("creationTime") is None:
                self.file_creation_time = None
            else:
                self.file_creation_time = isodate.parse_datetime(self.file_details["creationTime"])
            self.processing_status = self.processing_details.get("processingStatus")
            if self.processing_details.get("processingProgress") is None:
                self.processing_progress = None
            else:
                self.processing_progress = ProcessingProgress(self.processing_details["processingProgress"])
            self.processing_failure_reason: str = self.processing_details.get("processingFailureReason")
            self.file_details_availability: str = self.processing_details.get("fileDetailsAvailability")
            self.processing_issues_availability: str = self.processing_details.get("processingIssuesAvailability")
            self.tag_suggestions_availability: str = self.processing_details.get("tagSuggestionsAvailability")
            self.editor_suggestions_availability: str = self.processing_details.get("editorSuggestionsAvailability")
            self.thumbnails_availability: str = self.processing_details.get("thumbnailsAvailability")
            self.processing_errors: list[str] = self.suggestions.get("processingErrors")
            self.processing_warnings: list[str] = self.suggestions.get("processingWarnings")
            self.processing_hints: list[str] = self.suggestions.get("processingHints")
            if self.suggestions.get("tagSuggestions") is None:
                self.tag_suggestions = None
            else:
                self.tag_suggestions = \
                    [TagSuggestion(tag_suggestion) for tag_suggestion in self.suggestions.get("tagSuggestions")]
            self.editor_suggestions = self.suggestions.get("editorSuggestions")

        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)
