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
        self.default = YoutubeThumbnail(thumbnail_metadata["default"])
        self.medium = YoutubeThumbnail(thumbnail_metadata["medium"])
        self.high = YoutubeThumbnail(thumbnail_metadata["high"])
        self.standard = YoutubeThumbnail(thumbnail_metadata["standard"])
        self.maxres = YoutubeThumbnail(thumbnail_metadata["maxres"])


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
            self.id = raw_metadata["id"]
            self.url = f'https://www.youtube.com/playlist?list={self.id}'
            self.snippet = raw_metadata["snippet"]
            self.publish_date = self.snippet["publishedAt"]
            self.channel_id = self.snippet["channelId"]
            self.channel_url = f'https://www.youtube.com/channel/{self.channel_id}'
            self.title = self.snippet["title"]
            self.description = self.snippet["description"]
            self.thumbnail_data = self.snippet["thumbnails"]
            self.default_thumbnail = self.thumbnail_data["default"]
            self.default_thumbnail_url = self.default_thumbnail["url"]
            self.channel_name = self.snippet["channelTitle"]
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

    # async def get_duration(self):
    #     """fetches the duration separately because it requires a different api call"""
    #     async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as video_duration_session:
    #         async with video_duration_session.get(
    #                 f'https://www.googleapis.com/youtube/v{self.api_version}/videos?part=contentDetails'
    #                 f'&id={self.id}&maxResults=50&key={self.key}') as video_duration_response:
    #             if video_duration_response.status == 200:
    #                 res_data = await video_duration_response.json()
    #                 if "error" in res_data:
    #                     raise discord.HTTPException(video_duration_response, f'{res_data["error"].get("code")}:'
    #                                                                          f'{res_data["error"].get("message")}')
    #                 if res_data["pageInfo"].get("totalResults") < 1:
    #                     raise VideoNotFound(self.id)
    #                 else:
    #                     res_json = res_data.get("items")[0]
    #                     content_details = res_json.get("contentDetails")
    #                     return isodate.parse_duration(content_details.get("duration")).seconds
    #
    #             else:
    #                 message = f'The youtube API returned the following error code: {video_duration_response.status}'
    #                 if video_duration_response.content_type == "application/json":
    #                     res_data = await video_duration_response.json()
    #                     if "error" in res_data:
    #                         message = res_data["error"].get("message")
    #                 raise discord.HTTPException(video_duration_response, message)


