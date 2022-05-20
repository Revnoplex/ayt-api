import aiohttp
import discord
from .exceptions import PlaylistNotFound, InvalidInput, VideoNotFound
from .types import YoutubePlaylistSnippetMetadata, PlaylistVideoMetaData, VideoSnippetMetadata


class AsyncYoutubeAPI:
    def __init__(self, yt_api_key: str, api_version: str = '3'):
        self.key = yt_api_key
        self.api_version = api_version

    async def get_playlist_snippet_metadata(self, playlist_id: str):
        """Fetches a playlist using a playlist id"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as playlist_metadata_session:
            async with playlist_metadata_session.get(
                    f'https://www.googleapis.com/youtube/v{self.api_version}/playlists?part=snippet'
                    f'&id={playlist_id}&key={self.key}') as playlist_metadata_response:
                if playlist_metadata_response.status == 200:
                    res_data = await playlist_metadata_response.json()
                    if "error" in res_data:
                        raise discord.HTTPException(playlist_metadata_response, f'{res_data["error"].get("code")}:'
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
                    raise discord.HTTPException(playlist_metadata_response, message)

    async def get_videos_from_playlist(self, playlist_id, next_page=None):
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
                        raise discord.HTTPException(playlist_videos_response, f'{res_data["error"].get("code")}:'
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
                    raise discord.HTTPException(playlist_videos_response, message)

    async def get_video_snippet_metadata(self, video_id):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as video_duration_session:
            async with video_duration_session.get(
                    f'https://www.googleapis.com/youtube/v{self.api_version}/videos?part=snippet'
                    f'&id={video_id}&maxResults=50&key={self.key}') as video_duration_response:
                if video_duration_response.status == 200:
                    res_data = await video_duration_response.json()
                    if "error" in res_data:
                        raise discord.HTTPException(video_duration_response, f'{res_data["error"].get("code")}:'
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
                    raise discord.HTTPException(video_duration_response, message)


def strip_video_id(url: str):
    """supported urls:
    https://www.youtube.com/watch?v=ID

    https://www.youtube.com/v/ID

    https://youtu.be/ID"""
    if url.split('/')[2] == 'youtu.be':
        return url.split('/')[3].split("?")[0].split('&')[0]
    else:
        slash_index = 4 if url.split("/")[3] == "v" or url.split("/")[3] == "embed" else 3
        return url.split("/")[slash_index].replace("watch?v=", "").split("&")[0].split("?")[0]
