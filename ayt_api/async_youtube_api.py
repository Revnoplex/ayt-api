import aiohttp
from .exceptions import PlaylistNotFound, InvalidInput, VideoNotFound, HTTPException
from .types import YoutubePlaylistSnippetMetadata, PlaylistVideoMetaData, VideoSnippetMetadata


class AsyncYoutubeAPI:
    """Represents the main class for running all the tools
    Args:
        yt_api_key (str): The API key used to access the YouTube API
        api_version (str): The API version to use. defaults to 3"""
    def __init__(self, yt_api_key: str, api_version: str = '3'):
        self.key = yt_api_key
        self.api_version = api_version

    async def get_playlist_snippet_metadata(self, playlist_id: str) -> YoutubePlaylistSnippetMetadata:
        """Fetches a playlist snippet using a playlist id
        Args:
            playlist_id (str): The id of the playlist to use
        Returns:
            YoutubePlaylistSnippetMetadata: The playlist snippet object containing data of the playlist snippet
        Raises:
            HTTPException: Fetching the metadata failed
            PlaylistNotFound: The playlist does not exist"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as playlist_metadata_session:
            async with playlist_metadata_session.get(
                    f'https://www.googleapis.com/youtube/v{self.api_version}/playlists?part=snippet'
                    f'&id={playlist_id}&key={self.key}') as playlist_metadata_response:
                if playlist_metadata_response.status == 200:
                    res_data = await playlist_metadata_response.json()
                    if "error" in res_data:
                        raise HTTPException(playlist_metadata_response, f'{res_data["error"].get("code")}:'
                                                                        f'{res_data["error"].get("message")}')
                    if res_data["pageInfo"].get("totalResults") < 1:
                        raise PlaylistNotFound(playlist_id)
                    else:
                        res_json = res_data.get("items")[0]
                        return YoutubePlaylistSnippetMetadata(res_json)
                else:
                    message = f'The youtube API returned the following error code: {playlist_metadata_response.status}'
                    if playlist_metadata_response.content_type == "application/json":
                        res_data = await playlist_metadata_response.json()
                        if "error" in res_data:
                            message = res_data["error"].get("message")
                    raise HTTPException(playlist_metadata_response, message)

    async def get_videos_from_playlist(self, playlist_id, next_page=None) -> list[PlaylistVideoMetaData]:
        """Fetches a list of video in a playlist using a playlist id
        Args:
            playlist_id (str): The id of the playlist to use
            next_page: a parameter used by this function to fetch playlists with more than 50 items
        Returns:
            list[PlaylistVideoMetadata]: A list containing playlist video objects
        Raises:
            HTTPException: Fetching the metadata failed
            PlaylistNotFound: The playlist does not exist"""
        if len(playlist_id) < 1:
            raise InvalidInput(playlist_id)
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as playlist_videos_session:
            next_page_query = "" if next_page is None else f'&pageToken={next_page}'
            async with playlist_videos_session.get(f'https://www.googleapis.com/youtube/v{self.api_version}/'
                                                   f'playlistItems?part=snippet'
                                                   f'&playlistId={playlist_id}{next_page_query}&maxResults=500'
                                                   f'&key={self.key}') as playlist_videos_response:
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
                                                                                   next_page=res_data["nextPageToken"])
                        video_data = []
                        for result in res_json:
                            if result.get('snippet')['thumbnails']:
                                metadata_object = PlaylistVideoMetaData(result.get("snippet"))
                                video_data.append(metadata_object)
                        return video_data + videos_next_page
                elif playlist_videos_response.status == 404:
                    raise PlaylistNotFound(playlist_id)
                else:
                    message = f'The youtube API returned the following error code: {playlist_videos_response.status}'
                    if playlist_videos_response.content_type == "application/json":
                        res_data = await playlist_videos_response.json()
                        if "error" in res_data:
                            message = res_data["error"].get("message")
                    raise HTTPException(playlist_videos_response, message)

    async def get_video_snippet_metadata(self, video_id) -> VideoSnippetMetadata:
        """Fetches a video snippet using a video id
        Args:
            video_id (str): The id of the video to use
        Returns:
            VideoSnippetMetadata: The video snippet object containing data of the video snippet
        Raises:
            HTTPException: Fetching the metadata failed
            VideoNotFound: The video does not exist"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as video_duration_session:
            async with video_duration_session.get(
                    f'https://www.googleapis.com/youtube/v{self.api_version}/videos?part=snippet'
                    f'&id={video_id}&maxResults=50&key={self.key}') as video_duration_response:
                if video_duration_response.status == 200:
                    res_data = await video_duration_response.json()
                    if "error" in res_data:
                        raise HTTPException(video_duration_response, f'{res_data["error"].get("code")}:'
                                                                     f'{res_data["error"].get("message")}')
                    if res_data["pageInfo"].get("totalResults") < 1:
                        raise VideoNotFound(video_id)
                    else:
                        res_json = res_data.get("items")[0]
                        return VideoSnippetMetadata(res_json)
                else:
                    message = f'The youtube API returned the following error code: {video_duration_response.status}'
                    if video_duration_response.content_type == "application/json":
                        res_data = await video_duration_response.json()
                        if "error" in res_data:
                            message = res_data["error"].get("message")
                    raise HTTPException(video_duration_response, message)
