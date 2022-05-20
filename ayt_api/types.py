import datetime
from .exceptions import MissingDataFromMetadata, VideoNotFound


class YoutubeThumbnail:
    def __init__(self, data: dict):
        self.raw_data = data
        self.url: str = data["url"]
        self.width: int = data["width"]
        self.height: int = data["height"]
        self.resolution = "{}x{}".format(self.width, self.height)


class YoutubeThumbnailMetadata:
    def __init__(self, thumbnail_metadata: dict):
        self.raw_metadata = thumbnail_metadata

    @property
    def default(self):
        if self.raw_metadata.get("default") is not None:
            return YoutubeThumbnail(self.raw_metadata["default"])

    @property
    def medium(self):
        if self.raw_metadata.get("medium") is not None:
            return YoutubeThumbnail(self.raw_metadata["medium"])

    @property
    def high(self):
        if self.raw_metadata.get("high") is not None:
            return YoutubeThumbnail(self.raw_metadata["high"])

    @property
    def standard(self):
        if self.raw_metadata.get("standard") is not None:
            return YoutubeThumbnail(self.raw_metadata["standard"])

    @property
    def maxres(self):
        if self.raw_metadata.get("maxres") is not None:
            return YoutubeThumbnail(self.raw_metadata["maxres"])


class LocalName:
    def __init__(self, data: dict):
        self.raw_data = data
        self.title: str = data["title"]
        self.description: str = data["description"]


class YoutubePlaylistSnippetMetadata:
    """Data class for YouTube playlists"""
    def __init__(self, raw_metadata: dict):
        try:
            self.raw_metadata = raw_metadata
            self.id: str = raw_metadata["id"]
            self.url: str = f'https://www.youtube.com/playlist?list={self.id}'
            self.snippet: dict = raw_metadata["snippet"]
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
            if self.snippet.get("thumbnails") is None:
                self.thumbnails = None
            else:
                self.thumbnails = YoutubeThumbnailMetadata(self.snippet.get("thumbnails"))
            self.channel_name: str = self.snippet.get("channelTitle")
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), raw_metadata, missing_snippet_data)


class ABCVideoMetadata:
    pass


class PlaylistVideoMetaData(ABCVideoMetadata):
    """A data class for videos in a playlist"""
    def __init__(self, metadata):
        try:
            self.metadata = metadata
            self.position = metadata.get("position")
            self.id = metadata.get("resourceId")["videoId"]
            self.url = f'https://www.youtube.com/watch?v={self.id}'
            self.title = metadata.get("title")
            self.description = metadata.get('description')
            self.thumbnails = YoutubeThumbnailMetadata(metadata["thumbnails"])
            self.uploader_id = metadata.get("videoOwnerChannelId")
            self.uploader = metadata.get("videoOwnerChannelTitle")
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)


class VideoSnippetMetadata(ABCVideoMetadata):
    def __init__(self, metadata: dict):
        try:
            self.metadata = metadata
            self.snippet: dict = metadata["snippet"]
            self.id: str = metadata["id"]
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
            if self.snippet.get("thumbnails") is None:
                self.thumbnails = None
            else:
                self.thumbnails = YoutubeThumbnailMetadata(self.snippet.get("thumbnails"))
            self.channel_title: str = self.snippet.get("channelTitle")
            self.tags: list = self.snippet.get("tags")
            self.category_id: str = self.snippet.get("categoryId")
            self.live_broadcast_content: str = self.snippet.get("liveBroadcastContent")
            self.default_language: str = self.snippet.get("defaultLanguage")
            if self.snippet.get("localized") is None:
                self.localized = None
                self.localised = None
            self.localized = LocalName(self.snippet["localized"])
            self.localised = LocalName(self.snippet["localized"])
            self.default_audio_language: str = self.snippet.get("defaultAudioLanguage")
        except KeyError as missing_snippet_data:
            raise MissingDataFromMetadata(str(missing_snippet_data), metadata, missing_snippet_data)


