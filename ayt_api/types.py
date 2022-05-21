import datetime
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
        title (str): The title in a local language
        description (str): The description in a local language
    """
    def __init__(self, data: dict):
        """
        Args:
            data (dict): The raw local text data
        """
        self.data = data
        self.title: str = data.get("title")
        self.description: str = data.get("description")


class YoutubePlaylistSnippetMetadata:
    """Data class for YouTube playlists
    Attributes:
        metadata (dict): The raw API response used to construct this class
        id (str): The ID of the playlist. Example: "PLwZcI0zn-Jhemx2m_gpYqQfnc3l4xA4fp" from the url:
            "https://www.youtube.com/playlist?list=PLwZcI0zn-Jhemx2m_gpYqQfnc3l4xA4fp"
        url (str): The URL of the playlist
        snippet (str): The raw snippet data used to construct this class
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
    """
    def __init__(self, metadata: dict):
        """
        Args:
            metadata (dict): The raw API response to provide
        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided
        """
        try:
            self.metadata = metadata
            self.id: str = metadata["id"]
            self.url: str = f'https://www.youtube.com/playlist?list={self.id}'
            self.snippet: dict = metadata["snippet"]
            if self.snippet.get("publishedAt") is None:
                self.published_at = None
            else:
                self.published_at = datetime.datetime.strptime(self.snippet["publishedAt"], '%Y-%m-%dT%H:%M:%SZ')
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
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)


class ABCVideoMetadata:
    pass


class PlaylistVideoMetaData(ABCVideoMetadata):
    """A data class for videos in a playlist
    Attributes:
        metadata (dict): The raw metadata from the API call used to construct this class
        id (str): The ID of the video in the playlist. Example: "dQw4w9WgXcQ" from the url:
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ". Look familiar?
        position (int): The position in the playlist the video is in
        url (str): The URL of the video
        title (str): The title of the video
        description (str): The description of the video
        published_at (datetime.datetime): The date and time the video was published
        thumbnails (YoutubeThumbnailMetadata): The available thumbnails the video has
        channel_title: (str) The name of the channel that the video belongs to
        channel_id (str): The id of the channel that the video belongs to
        channel_url (str): The url of the channel that the video belongs to
    """
    def __init__(self, metadata: dict):
        """
        Args:
            metadata: The snippet metadata of the video in the playlist
        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided
        """
        try:
            self.metadata = metadata
            if metadata.get("publishedAt") is None:
                self.published_at = None
            else:
                self.published_at = datetime.datetime.strptime(metadata["publishedAt"], '%Y-%m-%dT%H:%M:%SZ')
            self.position: int = metadata.get("position")
            self.id: str = metadata.get("resourceId")["videoId"]
            self.url: str = f'https://www.youtube.com/watch?v={self.id}'
            self.title: str = metadata.get("title")
            self.description: str = metadata.get('description')
            self.thumbnails = YoutubeThumbnailMetadata(metadata["thumbnails"])
            self.channel_id: str = metadata.get("videoOwnerChannelId")
            if self.channel_id is None:
                self.channel_url = None
            else:
                self.channel_url: str = f'https://www.youtube".com/channel/{self.channel_id}'
            self.channel_title: str = metadata.get("videoOwnerChannelTitle")
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)


class VideoSnippetMetadata(ABCVideoMetadata):
    """A data class containing basic video data such as the title, id, description and channel
        Attributes:
            metadata (dict): The raw API response used to construct this class
            id (str): The ID of the video. Example: "dQw4w9WgXcQ" from the url:
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ". Look familiar?
            snippet (str): The raw snippet data used to construct this class
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
        """
    def __init__(self, metadata: dict):
        """
        Args:
            metadata: The snippet metadata of the video in the playlist
        Raises:
            MissingDataFromMetaData: There is malformed data in the metadata provided
        """
        try:
            self.metadata = metadata
            self.snippet: dict = metadata["snippet"]
            self.id: str = metadata["id"]
            self.url: str = f'https://www.youtube.com/watch?v={self.id}'
            if self.snippet.get("publishedAt") is None:
                self.published_at = None
            else:
                self.published_at = datetime.datetime.strptime(self.snippet["publishedAt"], '%Y-%m-%dT%H:%M:%SZ')
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
                self.localised = None
            else:
                self.localised = LocalName(self.snippet["localized"])
                self.localized = self.localised
            self.default_audio_language: str = self.snippet.get("defaultAudioLanguage")
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)
