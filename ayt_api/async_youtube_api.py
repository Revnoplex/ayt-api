import asyncio
import aiohttp
from .exceptions import PlaylistNotFound, InvalidInput, VideoNotFound, HTTPException, APITimeout
from .types import YoutubePlaylistMetadata, PlaylistVideoMetadata, YoutubeVideoMetadata


class AsyncYoutubeAPI:
    """Represents the main class for running all the tools
    Attributes:
        key (str): The API key used to access the YouTube API. To get an API key,
            see instructions here: https://developers.google.com/youtube/v3/getting-started
        api_version (str): The API version to use. defaults to 3
        call_url_prefix (str): The start of the youtube API call url to use
        timeout (ClientTimeout): The timeout if the api does not respond
    """
    def __init__(self, yt_api_key: str, api_version: str = '3', timeout: int = 5):
        """
        Args:
            yt_api_key (str): The API key used to access the YouTube API
            api_version (str): The API version to use. defaults to 3
            timeout (int): The timeout if the api does not respond
        """
        self.key = yt_api_key
        self.api_version = api_version
        self.call_url_prefix = f'https://www.googleapis.com/youtube/v{self.api_version}'
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def get_playlist_metadata(self, playlist_id: str) -> YoutubePlaylistMetadata:
        """Fetches playlist metadata using a playlist id

        Playlist metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubePlaylistMetadata` object

        Args:
            playlist_id (str): The id of the playlist to use
        Returns:
            YoutubePlaylistMetadata: The playlist object containing data of the playlist
        Raises:
            HTTPException: Fetching the metadata failed
            PlaylistNotFound: The playlist does not exist
            aiohttp.ClientError: There was a problem sending the request to the api
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as playlist_metadata_session:
            call_url = f'{self.call_url_prefix}/playlists?part=snippet&part=status&part=contentDetails&part=player' \
                       f'&part=localizations&id={playlist_id}&key={self.key}'
            try:
                async with playlist_metadata_session.get(call_url) as playlist_metadata_response:
                    if playlist_metadata_response.status == 200:
                        res_data = await playlist_metadata_response.json()
                        if "error" in res_data:
                            raise HTTPException(playlist_metadata_response, f'{res_data["error"].get("code")}:'
                                                                            f'{res_data["error"].get("message")}')
                        if res_data["pageInfo"].get("totalResults") < 1:
                            raise PlaylistNotFound(playlist_id)
                        else:
                            res_json = res_data.get("items")[0]
                            return YoutubePlaylistMetadata(res_json, call_url)
                    else:
                        message = f'The youtube API returned the following error code: ' \
                                  f'{playlist_metadata_response.status}'
                        if playlist_metadata_response.content_type == "application/json":
                            res_data = await playlist_metadata_response.json()
                            if "error" in res_data:
                                error_data = res_data["error"]
                                message = error_data.get("message")
                        raise HTTPException(playlist_metadata_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    async def get_videos_from_playlist(self, playlist_id, next_page=None) -> list[PlaylistVideoMetadata]:
        """Fetches a list of video in a playlist using a playlist id

        Playlist video metadata is fetched using a GET request which the response is then concentrated into a list of
        :class:`PlaylistVideoMetadata` objects

        Args:
            playlist_id (str): The id of the playlist to use
            next_page: a parameter used by this function to fetch playlists with more than 50 items
        Returns:
            list[PlaylistVideoMetadata]: A list containing playlist video objects
        Raises:
            HTTPException: Fetching the metadata failed
            PlaylistNotFound: The playlist does not exist
            aiohttp.ClientError: There was a problem sending the request to the api
        """
        if len(playlist_id) < 1:
            raise InvalidInput(playlist_id)
        async with aiohttp.ClientSession(timeout=self.timeout) as playlist_videos_session:
            next_page_query = "" if next_page is None else f'&pageToken={next_page}'
            call_url = f'{self.call_url_prefix}/playlistItems?part=snippet&part=contentDetails&part=status' \
                       f'&playlistId={playlist_id}{next_page_query}&maxResults=500&key={self.key}'
            try:
                async with playlist_videos_session.get(call_url) as playlist_videos_response:
                    if playlist_videos_response.status == 200:
                        res_data = await playlist_videos_response.json()
                        if "error" in res_data:
                            raise HTTPException(playlist_videos_response, f'{res_data["error"].get("code")}:'
                                                                          f'{res_data["error"].get("message")}')
                        if res_data["pageInfo"].get("totalResults") < 1:
                            raise PlaylistNotFound(playlist_id)
                        else:
                            res_json = res_data.get("items")
                            videos_next_page = []
                            if res_data.get("nextPageToken") is not None:
                                videos_next_page = await self.get_videos_from_playlist(playlist_id,
                                                                                       next_page=
                                                                                       res_data["nextPageToken"])
                            videos = [PlaylistVideoMetadata(vid_item, call_url) for vid_item in res_json]
                            return videos + videos_next_page
                    elif playlist_videos_response.status == 404:
                        raise PlaylistNotFound(playlist_id)
                    else:
                        message = f'The youtube API returned the following error code: ' \
                                  f'{playlist_videos_response.status}'
                        if playlist_videos_response.content_type == "application/json":
                            res_data = await playlist_videos_response.json()
                            if "error" in res_data:
                                error_data = res_data["error"]
                                message = error_data.get("message")
                        raise HTTPException(playlist_videos_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    async def get_video_metadata(self, video_id) -> YoutubeVideoMetadata:
        """Fetches information on a video using a video id

        Video metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeVideoMetadata` object

        Args:
            video_id (str): The id of the video to use
        Returns:
            YoutubeVideoMetadata: The video object containing data of the video
        Raises:
            HTTPException: Fetching the metadata failed
            VideoNotFound: The video does not exist
            aiohttp.ClientError: There was a problem sending the request to the api
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as video_duration_session:
            call_url = f'{self.call_url_prefix}/videos?part=snippet&part=contentDetails&part=status&part=statistics' \
                       f'&part=player&part=topicDetails&part=recordingDetails&part=liveStreamingDetails' \
                       f'&part=localizations&id={video_id}&maxResults=50&key={self.key}'
            try:
                async with video_duration_session.get(call_url) as video_response:
                    if video_response.status == 200:
                        res_data = await video_response.json()
                        if "error" in res_data:
                            raise HTTPException(video_response, f'{res_data["error"].get("code")}:'
                                                                f'{res_data["error"].get("message")}')
                        if res_data["pageInfo"].get("totalResults") < 1:
                            raise VideoNotFound(video_id)
                        else:
                            res_json = res_data.get("items")[0]
                            return YoutubeVideoMetadata(res_json, call_url)
                    else:
                        message = f'The youtube API returned the following error code: {video_response.status}'
                        if video_response.content_type == "application/json":
                            res_data = await video_response.json()
                            error_data = res_data["error"]
                            message = error_data.get("message")
                        raise HTTPException(video_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)
