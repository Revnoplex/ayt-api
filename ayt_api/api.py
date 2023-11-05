import asyncio
from typing import Optional
import aiohttp
from aiohttp import TCPConnector
from .exceptions import PlaylistNotFound, InvalidInput, VideoNotFound, HTTPException, APITimeout, ChannelNotFound, \
    CommentNotFound
from .types import YoutubePlaylistMetadata, PlaylistVideoMetadata, YoutubeVideoMetadata, YoutubeChannelMetadata, \
    YoutubeCommentThread, YoutubeComment


class AsyncYoutubeAPI:
    """Represents the main class for running all the tools
    Attributes:
        key (str): The API key used to access the YouTube API. To get an API key,
            see instructions here: https://developers.google.com/youtube/v3/getting-started
        api_version (str):
            The API version to use. defaults to 3
        call_url_prefix (str): The start of the YouTube API call url to use
        timeout (ClientTimeout): The timeout if the api does not respond
        ignore_ssl (bool): whether to ignore any verification errors with the ssl certificate.
                This is useful for using the api on a restricted network.
    """
    def __init__(self, yt_api_key: str, api_version: str = '3', timeout: int = 5, ignore_ssl: bool = False):
        """
        Args:
            yt_api_key (str): The API key used to access the YouTube API
            api_version (str): The API version to use. defaults to 3
            timeout (int): The timeout if the api does not respond
            ignore_ssl (bool): whether to ignore any verification errors with the ssl certificate.
                This is useful for using the api on a restricted network.
        """
        self.key = yt_api_key
        self.api_version = api_version
        self.call_url_prefix = f'https://www.googleapis.com/youtube/v{self.api_version}'
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.ignore_ssl = ignore_ssl

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
            InvalidInput: The input is not a playlist id
            APITimeout: The YouTube api did not respond within the timeout period set
        """
        if len(playlist_id) < 1:
            raise InvalidInput(playlist_id)
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout) \
                as playlist_metadata_session:
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
                            return YoutubePlaylistMetadata(res_json, call_url, self)
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

    async def get_videos_from_playlist(self, playlist_id: str, next_page: str = None) -> list[PlaylistVideoMetadata]:
        """Fetches a list of video in a playlist using a playlist id

        Playlist video metadata is fetched using a GET request which the response is then concentrated into a list of
        :class:`PlaylistVideoMetadata` objects

        Args:
            playlist_id (str): The id of the playlist to use
            next_page (str): a parameter used by this function to fetch playlists with more than 50 items
        Returns:
            list[PlaylistVideoMetadata]: A list containing playlist video objects
        Raises:
            HTTPException: Fetching the metadata failed
            PlaylistNotFound: The playlist does not exist
            aiohttp.ClientError: There was a problem sending the request to the api
            InvalidInput: The input is not a playlist id
            APITimeout: The YouTube api did not respond within the timeout period set
        """
        if len(playlist_id) < 1:
            raise InvalidInput(playlist_id)
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout) \
                as playlist_videos_session:
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
                                videos_next_page = await self.get_videos_from_playlist(
                                    playlist_id, next_page=res_data["nextPageToken"])
                            videos = [PlaylistVideoMetadata(vid_item, call_url, self) for vid_item in res_json]
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

    async def get_video_metadata(self, video_id: str) -> YoutubeVideoMetadata:
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
            InvalidInput: The input is not a playlist id
            APITimeout: The YouTube api did not respond within the timeout period set
        """
        if len(video_id) < 1:
            raise InvalidInput(video_id)
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout) \
                as video_session:
            call_url = f'{self.call_url_prefix}/videos?part=snippet&part=contentDetails&part=status&part=statistics' \
                       f'&part=player&part=topicDetails&part=recordingDetails&part=liveStreamingDetails' \
                       f'&part=localizations&id={video_id}&maxResults=50&key={self.key}'
            try:
                async with video_session.get(call_url) as video_response:
                    if video_response.status == 200:
                        res_data = await video_response.json()
                        if "error" in res_data:
                            raise HTTPException(video_response, f'{res_data["error"].get("code")}:'
                                                                f'{res_data["error"].get("message")}')
                        if res_data["pageInfo"].get("totalResults") < 1:
                            raise VideoNotFound(video_id)
                        else:
                            res_json = res_data.get("items")[0]
                            return YoutubeVideoMetadata(res_json, call_url, self)
                    else:
                        message = f'The youtube API returned the following error code: {video_response.status}'
                        if video_response.content_type == "application/json":
                            res_data = await video_response.json()
                            error_data = res_data["error"]
                            message = error_data.get("message")
                        raise HTTPException(video_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    async def get_channel_metadata(self, channel_id: str) -> YoutubeChannelMetadata:
        """Fetches information on a channel using a channel id

        Channel metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeChannelMetadata` object

        Args:
            channel_id (str): The id of the channel to use
        Returns:
            YoutubeChannelMetadata: The channel object containing data of the channel
        Raises:
            HTTPException: Fetching the metadata failed
            ChannelNotFound: The channel does not exist
            aiohttp.ClientError: There was a problem sending the request to the api
            InvalidInput: The input is not a playlist id
            APITimeout: The YouTube api did not respond within the timeout period set
        """
        if len(channel_id) < 1:
            raise InvalidInput(channel_id)
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout) \
                as channel_session:
            call_url = f'{self.call_url_prefix}/channels?part=snippet&part=contentDetails&part=status&part=statistics' \
                       f'&part=topicDetails&part=brandingSettings&part=contentOwnerDetails' \
                       f'&part=localizations&part=id&id={channel_id}&maxResults=50&key={self.key}'
            try:
                async with channel_session.get(call_url) as channel_response:
                    if channel_response.status == 200:
                        res_data = await channel_response.json()
                        if "error" in res_data:
                            raise HTTPException(channel_response, f'{res_data["error"].get("code")}:'
                                                                  f'{res_data["error"].get("message")}')
                        if res_data["pageInfo"].get("totalResults") < 1:
                            raise ChannelNotFound(channel_id)
                        else:
                            res_json = res_data.get("items")[0]
                            return YoutubeChannelMetadata(res_json, call_url, self)
                    else:
                        message = f'The youtube API returned the following error code: {channel_response.status}'
                        if channel_response.content_type == "application/json":
                            res_data = await channel_response.json()
                            error_data = res_data["error"]
                            message = error_data.get("message")
                        raise HTTPException(channel_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    async def get_video_comments(self, video_id: str, max_comments: Optional[int] = 50, next_page: str = None,
                                 current_count=0) -> list[YoutubeCommentThread]:
        """Fetches comments on a video

        A list of comment threads are fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeCommentThread` object

        Args:
            video_id (str): The id of the video to use
            max_comments (int): The maximum number of comments to fetch. Specify ``None`` to fetch all comments.
                                WARNING! specifying a high number or ``None`` could hammer the api too much causing you
                                to get rate limited so do this with caution
            next_page (str): A parameter used by this function to fetch more than 21 comments
            current_count (int): A parameter used by this function to track how many comments are fetched to satisfy
                                 the :param:`max_comments` parameter
        Returns:
            list[YoutubeCommentThread]: A list of comments as YoutubeCommentThreads
        Raises:
            HTTPException: Fetching the metadata failed
            VideoNotFound: The video to look for comments on does not exist
            aiohttp.ClientError: There was a problem sending the request to the api
            InvalidInput: The input is not a playlist id
            APITimeout: The YouTube api did not respond within the timeout period set
        """
        if len(video_id) < 1:
            raise InvalidInput(video_id)
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout) \
                as thread_session:
            next_page_query = "" if next_page is None else f'&pageToken={next_page}'
            call_url = f'{self.call_url_prefix}/commentThreads?part=snippet&part=replies&part=id&videoId={video_id}' \
                       f'{next_page_query}&maxResults=50&key={self.key}'
            try:
                async with thread_session.get(call_url) as thread_response:
                    if thread_response.status == 200:
                        res_data = await thread_response.json()
                        if "error" in res_data:
                            if 'videoNotFound' in [error.get("reason") for error in res_data["error"]["errors"]]:
                                raise VideoNotFound(video_id)
                            raise HTTPException(thread_response, f'{res_data["error"].get("code")}:'
                                                                 f'{res_data["error"].get("message")}')
                        res_json = res_data.get("items")
                        videos_next_page = []
                        if res_data.get("nextPageToken") is not None:
                            current_count += res_data["pageInfo"].get("totalResults")
                            if not max_comments or current_count < max_comments:
                                videos_next_page = await self.get_video_comments(
                                    video_id, next_page=res_data["nextPageToken"], current_count=current_count,
                                    max_comments=max_comments)
                        videos = [YoutubeCommentThread(item, call_url, self) for item in res_json]
                        return (videos + videos_next_page)[:max_comments]
                    else:
                        message = f'The youtube API returned the following error code: {thread_response.status}'
                        if thread_response.content_type == "application/json":
                            res_data = await thread_response.json()
                            error_data = res_data["error"]
                            if 'videoNotFound' in [error.get("reason") for error in error_data["errors"]]:
                                raise VideoNotFound(video_id)
                            message = error_data.get("message")
                        raise HTTPException(thread_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    async def get_channel_comments(self, channel_id: str, max_comments: Optional[int] = 50, next_page: str = None,
                                   current_count=0) -> list[YoutubeCommentThread]:
        """Fetches comments on an entire channel

        A list of comment threads are fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeCommentThread` object

        Args:
            channel_id (str): The id of the channel to use
            max_comments (int): The maximum number of comments to fetch. Specify ``None`` to fetch all comments.
                                WARNING! specifying a high number or ``None`` could hammer the api too much causing you
                                to get rate limited so do this with caution
            next_page (str): A parameter used by this function to fetch more than 21 comments
            current_count (int): A parameter used by this function to track how many comments are fetched to satisfy
                                 the :param:`max_comments` parameter
        Returns:
            list[YoutubeCommentThread]: A list of comments as YoutubeCommentThreads
        Raises:
            HTTPException: Fetching the metadata failed
            VideoNotFound: The video to look for comments on does not exist
            aiohttp.ClientError: There was a problem sending the request to the api
            InvalidInput: The input is not a playlist id
            APITimeout: The YouTube api did not respond within the timeout period set
        """
        if len(channel_id) < 1:
            raise InvalidInput(channel_id)
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout) \
                as thread_session:
            next_page_query = "" if next_page is None else f'&pageToken={next_page}'
            call_url = f'{self.call_url_prefix}/commentThreads?part=snippet&part=replies&part=id&' \
                       f'allThreadsRelatedToChannelId={channel_id}{next_page_query}&maxResults=50&key={self.key}'
            try:
                async with thread_session.get(call_url) as thread_response:
                    if thread_response.status == 200:
                        res_data = await thread_response.json()
                        if "error" in res_data:
                            if 'channelNotFound' in [error.get("reason") for error in res_data["error"]["errors"]]:
                                raise ChannelNotFound(channel_id)
                            raise HTTPException(thread_response, f'{res_data["error"].get("code")}:'
                                                                 f'{res_data["error"].get("message")}')
                        res_json = res_data.get("items")
                        videos_next_page = []
                        if res_data.get("nextPageToken") is not None:
                            current_count += res_data["pageInfo"].get("totalResults")
                            if not max_comments or current_count < max_comments:
                                videos_next_page = await self.get_video_comments(
                                    channel_id, next_page=res_data["nextPageToken"], current_count=current_count,
                                    max_comments=max_comments)
                        videos = [YoutubeCommentThread(item, call_url, self) for item in res_json]
                        return (videos + videos_next_page)[:max_comments]
                    else:
                        message = f'The youtube API returned the following error code: {thread_response.status}'
                        if thread_response.content_type == "application/json":
                            res_data = await thread_response.json()
                            error_data = res_data["error"]
                            if 'channelNotFound' in [error.get("reason") for error in error_data["errors"]]:
                                raise ChannelNotFound(channel_id)
                            message = error_data.get("message")
                        raise HTTPException(thread_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    async def get_comment_metadata(self, comment_id: str) -> YoutubeComment:
        """Fetches individual comments

        comments are fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeComment` object

        Args:
            comment_id (str): The id of the comment to use
        Returns:
            YoutubeComment: The YouTube comment object
        Raises:
            HTTPException: Fetching the metadata failed
            VideoNotFound: The video does not exist
            aiohttp.ClientError: There was a problem sending the request to the api
            InvalidInput: The input is not a playlist id
            APITimeout: The YouTube api did not respond within the timeout period set
        """
        if len(comment_id) < 1:
            raise InvalidInput(comment_id)
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout) \
                as comment_session:
            call_url = f'{self.call_url_prefix}/comments?part=snippet&part=id&id={comment_id}' \
                       f'&key={self.key}'
            print(call_url)
            try:
                async with comment_session.get(call_url) as comment_response:
                    if comment_response.status == 200:
                        res_data = await comment_response.json()
                        if "error" in res_data:
                            raise HTTPException(comment_response, f'{res_data["error"].get("code")}:'
                                                                  f'{res_data["error"].get("message")}')
                        if len(res_data.get("items")) < 1:
                            raise CommentNotFound(comment_id)
                        else:
                            res_json = res_data.get("items")[0]
                            return YoutubeComment(res_json, call_url, self)
                    else:
                        message = f'The youtube API returned the following error code: {comment_response.status}'
                        if comment_response.content_type == "application/json":
                            res_data = await comment_response.json()
                            error_data = res_data["error"]
                            message = error_data.get("message")
                        raise HTTPException(comment_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    async def fetch_comment_replies(self, comment_id: str, max_comments: Optional[int] = 50, next_page: str = None,
                                    current_count=0) -> list[YoutubeComment]:
        """Fetches a list of replies on a comment

        comments are fetched using a GET request which the response is then concentrated into a
        :class:`list[YoutubeComment]` object

        Args:
            comment_id (str): The id of the comment to use
            max_comments (int): The maximum number of comments to fetch. Specify ``None`` to fetch all comments.
                                WARNING! specifying a high number or ``None`` could hammer the api too much causing you
                                to get rate limited so do this with caution
            next_page (str): A parameter used by this function to fetch more than 21 comments
            current_count (int): A parameter used by this function to track how many comments are fetched to satisfy
                                 the :param:`max_comments` parameter
        Returns:
            list[YoutubeComment]: The replies on the comment
        Raises:
            HTTPException: Fetching the metadata failed
            aiohttp.ClientError: There was a problem sending the request to the api
            InvalidInput: The input is not a playlist id
            APITimeout: The YouTube api did not respond within the timeout period set
        """
        if len(comment_id) < 1:
            raise InvalidInput(comment_id)
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout) \
                as comment_session:
            next_page_query = "" if next_page is None else f'&pageToken={next_page}'
            call_url = f'{self.call_url_prefix}/comments?part=snippet&part=id&parentId={comment_id}' \
                       f'{next_page_query}&key={self.key}'
            try:
                async with comment_session.get(call_url) as comment_response:
                    if comment_response.status == 200:
                        res_data = await comment_response.json()
                        if "error" in res_data:
                            raise HTTPException(comment_response, f'{res_data["error"].get("code")}:'
                                                                  f'{res_data["error"].get("message")}')
                        res_json = res_data.get("items")
                        comments_next_page = []
                        if res_data.get("nextPageToken") is not None:
                            current_count += len(res_json)
                            if not max_comments or current_count < max_comments:
                                comments_next_page = await self.fetch_comment_replies(
                                    comment_id, next_page=res_data["nextPageToken"], current_count=current_count,
                                    max_comments=max_comments)
                        comments = [YoutubeComment(item, call_url, self) for item in res_json]
                        return (comments + comments_next_page)[:max_comments]
                    else:
                        message = f'The youtube API returned the following error code: {comment_response.status}'
                        if comment_response.content_type == "application/json":
                            res_data = await comment_response.json()
                            error_data = res_data["error"]
                            message = error_data.get("message")
                        raise HTTPException(comment_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)
