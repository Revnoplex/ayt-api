import asyncio
import datetime
import os
import pathlib
from typing import Optional, Union, Any
from urllib import parse

import aiohttp
from aiohttp import TCPConnector
from .exceptions import PlaylistNotFound, InvalidInput, VideoNotFound, HTTPException, APITimeout, ChannelNotFound, \
    CommentNotFound, ResourceNotFound
from .types import YoutubePlaylist, PlaylistItem, YoutubeVideo, YoutubeChannel, YoutubeCommentThread, \
    YoutubeComment, YoutubeSearchResult, REFERENCE_TABLE, VideoCaption
from .filters import SearchFilter
from .utils import censor_token, snake_to_camel


class AsyncYoutubeAPI:
    """Represents the main class for running all the tools.

    Attributes:
        api_version (str): The API version to use. defaults to 3.
        call_url_prefix (str): The start of the YouTube API call url to use.
        timeout (ClientTimeout): The timeout if the api does not respond.
        ignore_ssl (bool): Whether to ignore any verification errors with the ssl certificate.
            This is useful for using the api on a restricted network.
    """
    URL_PREFIX = "https://www.googleapis.com/youtube/v{version}"

    def __init__(self, yt_api_key: str, api_version: str = '3', timeout: int = 5, ignore_ssl: bool = False):
        """
        Args:
            yt_api_key (str): The API key used to access the YouTube API. to get an API key.
                See instructions here: https://developers.google.com/youtube/v3/getting-started
            api_version (str): The API version to use. defaults to 3.
            timeout (int): The timeout if the api does not respond.
            ignore_ssl (bool): Whether to ignore any verification errors with the ssl certificate.
                This is useful for using the api on a restricted network.
        """
        self._key = yt_api_key
        self.api_version = api_version
        self.call_url_prefix = self.URL_PREFIX.format(version=self.api_version)
        self._skeleton_url = self.call_url_prefix + "/{kind}?part={parts}{queries}&key=" + self._key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.ignore_ssl = ignore_ssl

    async def _call_api(self, call_type: str, query: str, ids: Union[str, list[str]], parts: list[str],
                        return_type: type, exception_type: type[ResourceNotFound], max_results: int = None,
                        max_items: int = None, multi_resp=False, next_page: str = None,
                        next_list: list[str] = None,
                        current_count=0, expected_count=1, other_queries: str = None) -> Union[Any, list]:
        """A centralised function for calling the api.
        Args:
            call_type (str): The type of request to make to the YouTube api.
            query (str): The variable name for the :param:`ids` (identifier keywords).
            ids (Union[str, list[str]]): The identifier keywords (usually IDs to look for).
            parts (list[str]): A list of parts to request of the main request.
            return_type (type): The object to return the results in.
            exception_type (type[ResourceNotFound]): The exception to raise if the item wanted was not found.
            max_results (Optional[int]): The maximum results per page.
            max_items (Optional[int]): The exact maximum of items to finally return.
            multi_resp (bool): Whether the type of api call is always expected to return multiple items.
            next_page (Optional[str]): The page token used to get the items in a followup api call.
            next_list (Optional[list[str]]): The identifier keywords remaining (if over 50) to use in a followup api
                call.
            current_count (int): The sum of items returned each api request.
            expected_count (int): The number of items expected to be returned by the api that were requested.
            other_queries (Optional[str]): Additional query strings to use in the call url.

        Returns:
            Union[Any, list]: The object specified in :param:`return_type`.

        Raises:
            HTTPException: Fetching the request failed.
            ResourceNotFound: The requested item was not found.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The query was empty.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        if len(ids) < 1:
            raise InvalidInput(ids)
        if isinstance(ids, str):
            multi = False
        elif isinstance(ids, list):
            multi = True
            expected_count = len(ids)
        else:
            raise InvalidInput(ids)
        if multi and len(ids) > 50:
            next_list = ids[50:]
            ids = ids[:50]
        async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout) \
                as yt_api_session:
            id_object = ",".join(ids) if multi else ids
            next_page_query = "" if next_page is None else f'&pageToken={next_page}'
            max_results_query = "" if max_results is None else f'&maxResults={max_results}'
            x_queries = "" if other_queries is None else other_queries
            call_url = self._skeleton_url.format(kind=call_type, parts=",".join(parts),
                                                 queries=f"&{query}={id_object}{x_queries}"
                                                         f"{next_page_query}{max_results_query}")
            try:
                async with yt_api_session.get(call_url) as yt_api_response:
                    if yt_api_response.ok:
                        res_data = await yt_api_response.json()
                        if "error" in res_data:
                            check = [error.get("reason") for error in res_data["error"]["errors"]
                                     if error.get("reason").endswith("NotFound")]
                            if check:
                                raise exception_type(ids)
                            raise HTTPException(yt_api_response, f'{res_data["error"].get("code")}: '
                                                                 f'{res_data["error"].get("message")}')
                        items = res_data.get("items") or []
                        returned_items = [item.get("id") if isinstance(item.get("id"), str) else None for item in items]
                        difference = list(set(ids).difference(set(returned_items)))
                        if (difference and multi) or (not multi_resp and len(items) < 1):
                            raise exception_type(difference if multi else ids)
                        else:
                            if multi or multi_resp:
                                items_next_page = []
                                if res_data.get("nextPageToken") is not None:
                                    current_count += len(res_data.get("items"))
                                    if not max_items or current_count < max_items:
                                        items_next_page = await self._call_api(call_type, query, ids, parts,
                                                                               return_type, exception_type, max_results,
                                                                               max_items, multi_resp,
                                                                               res_data["nextPageToken"],
                                                                               current_count=current_count,
                                                                               expected_count=expected_count)
                                items_next_list = []
                                if next_list:
                                    items_next_list = await self._call_api(call_type, query, next_list, parts,
                                                                           return_type, exception_type, max_results,
                                                                           max_items, multi_resp,
                                                                           expected_count=expected_count)
                                items = [return_type(item, call_url, self) for item in items]
                                return (items + items_next_page + items_next_list)[:max_items]
                            else:
                                res_json = res_data.get("items")[0]
                                return return_type(res_json, censor_token(call_url), self)
                    else:
                        message = f'The youtube API returned the following error code: ' \
                                  f'{yt_api_response.status}'
                        error_data = None
                        if yt_api_response.content_type == "application/json":
                            res_data = await yt_api_response.json()
                            if "error" in res_data:
                                check = [error.get("reason") for error in res_data["error"]["errors"]
                                         if error.get("reason").endswith("NotFound")]
                                if check:
                                    raise exception_type(ids)
                                error_data = res_data["error"]
                                message = error_data.get("message")
                        raise HTTPException(yt_api_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    async def download_thumbnail(self, thumbnail_url: str) -> bytes:
        """Downloads the thumbnail specified and stores it as a :class:`bytes` object

        Args:
            thumbnail_url (str): The i.ytimg.com asset url of the thumbnail
        Returns:
            bytes: The image as a :class:`bytes` object
        Raises:
            HTTPException: Fetching the request failed.
            aiohttp.ClientError: There was a problem sending the request to the api.
            RuntimeError: The contents was not a jpeg image
            asyncio.TimeoutError: The i.ytimg.com server did not respond within the timeout period set.
        """
        async with (aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout)
                    as thumbnail_session):
            async with thumbnail_session.get(thumbnail_url) as thumbnail_response:
                if not thumbnail_response.ok:
                    raise HTTPException(thumbnail_response)
                elif thumbnail_response.content_type != "image/jpeg":
                    raise RuntimeError("Received unexpected content type when attempting to download thumbnail")
                else:
                    return await thumbnail_response.read()

    async def save_thumbnail(self, thumbnail_url: str, fp: os.PathLike | str | None = None):
        """Downloads the thumbnail specified and saves it to a specified location

            Args:
                thumbnail_url (str): The i.ytimg.com asset url of the thumbnail
                fp (os.PathLike | str): The path and/or filename to save the file to.
                    Defaults to current working directory with the filename format: ``{video_id}-{quality}.png``
            Raises:
                HTTPException: Fetching the request failed.
                aiohttp.ClientError: There was a problem sending the request to the api.
                RuntimeError: The contents was not a jpeg image
                asyncio.TimeoutError: The i.ytimg.com server did not respond within the timeout period set.
        """
        thumbnail = await self.download_thumbnail(thumbnail_url)
        parsed_url = parse.urlparse(thumbnail_url)
        default_filename = parsed_url.path.split("/")[-2] + "-" + parsed_url.path.split("/")[-1]
        if isinstance(fp, str):
            fp = pathlib.Path(fp)
        path = (fp or pathlib.Path(default_filename)).expanduser()
        if path.is_dir():
            path = path.joinpath(default_filename)
        with open(path, "wb") as thumbnail_file:
            thumbnail_file.write(thumbnail)

    async def download_banner(self, banner_url: str) -> tuple[bytes, str]:
        # noinspection SpellCheckingInspection
        """Downloads the banner specified and stores it as a :class:`bytes` object

                Args:
                    banner_url (str): The yt3.googleusercontent.com asset url of the banner
                Returns:
                    tuple[bytes, str]: A list containing the image as a :class:`bytes` object and the file extension of
                        the image
                Raises:
                    HTTPException: Fetching the request failed.
                    aiohttp.ClientError: There was a problem sending the request to the api.
                    RuntimeError: The contents was not a jpeg image
                    asyncio.TimeoutError: The i.ytimg.com server did not respond within the timeout period set.
                """
        async with (aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout)
                    as thumbnail_session):
            async with thumbnail_session.get(banner_url) as thumbnail_response:
                if not thumbnail_response.ok:
                    raise HTTPException(thumbnail_response)
                else:
                    return await thumbnail_response.read(), thumbnail_response.content_type.split("/")[-1]

    async def save_banner(self, banner_url: str, fp: os.PathLike | str | None = None):
        """Downloads the banner specified and saves it to a specified location

            Args:
                banner_url (str): The i.ytimg.com asset url of the thumbnail
                fp (os.PathLike | str): The path and/or filename to save the file to.
                    Defaults to current working directory with the filename format: ``{video_id}-{quality}.png``
            Raises:
                HTTPException: Fetching the request failed.
                aiohttp.ClientError: There was a problem sending the request to the api.
                RuntimeError: The contents was not a jpeg image
                asyncio.TimeoutError: The i.ytimg.com server did not respond within the timeout period set.
        """
        banner, extension = await self.download_banner(banner_url)
        parsed_url = parse.urlparse(banner_url)
        default_filename = parsed_url.path.split("/")[-1] + "." + extension
        if isinstance(fp, str):
            fp = pathlib.Path(fp)
        path = (fp or pathlib.Path(default_filename)).expanduser()
        if path.is_dir():
            path = path.joinpath(default_filename)
        with open(path, "wb") as thumbnail_file:
            thumbnail_file.write(banner)

    async def fetch_playlist(self, playlist_id: Union[str, list[str]]) -> Union[YoutubePlaylist, list[YoutubePlaylist]]:
        """Fetches playlist metadata using a playlist id.

        Playlist metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubePlaylist` object.

        Args:
            playlist_id (str): The id of the playlist to use.

        Returns:
            Union[YoutubePlaylist, list[YoutubePlaylist]]: The playlist object containing data of the playlist.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api("playlists", "id", playlist_id,
                                    ["snippet", "status", "contentDetails", "player", "localizations"],
                                    YoutubePlaylist, PlaylistNotFound)

    async def fetch_playlist_items(self, playlist_id: str) -> list[PlaylistItem]:
        """Fetches a list of items in a playlist using a playlist id.

        Playlist video metadata is fetched using a GET request which the response is then concentrated into a list of
        :class:`PlaylistItem` objects.

        Args:
            playlist_id (str): The id of the playlist to use.

        Returns:
            list[PlaylistItem]: A list containing playlist video objects.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api("playlistItems", "playlistId", playlist_id, ["snippet", "status", "contentDetails"],
                                    PlaylistItem, PlaylistNotFound, 500, None, True)

    async def fetch_playlist_videos(self, playlist_id, exclude: list[str] = None) -> list[YoutubeVideo]:
        """Fetches a list of videos in a playlist using a playlist id.

        Playlist videos are fetched using a GET request which the response is then concentrated into a list of
        :class:`YoutubeVideo` objects.

        Args:
            playlist_id (str): The id of the playlist to use.
            exclude (Optional[list[str]]): A list of videos to not fetch in the playlist
        Returns:
            list[YoutubeVideo]: A list containing playlist video objects.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            VideoNotFound: A video in the playlist was unavailable.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        plist_items = await self.fetch_playlist_items(playlist_id)
        video_ids = [item.id for item in plist_items if item.id not in (exclude or [])]
        return await self.fetch_video(video_ids)

    async def fetch_video(self, video_id: Union[str, list[str]]) -> Union[YoutubeVideo, list[YoutubeVideo]]:
        """Fetches information on a video using a video id.

        Video metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeVideo` object if one ID was specified if more, it returns a list of them.

        Args:
            video_id (str): The id of the video to use.

        Returns:
            Union[YoutubeVideo, list[YoutubeVideo]]: The video object containing data of the video.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api("videos", "id", video_id, ["snippet", "status", "contentDetails", "statistics",
                                                               "player", "topicDetails", "recordingDetails",
                                                               "liveStreamingDetails", "localizations"], YoutubeVideo,
                                    VideoNotFound, 50)

    async def fetch_channel(self, channel_id: Union[str, list[str]]) -> Union[YoutubeChannel, list[YoutubeChannel]]:
        """Fetches information on a channel using a channel id.

        Channel metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeChannel` object or a list if multiple IDs were specified.

        Args:
            channel_id (str): The id of the channel to use.

        Returns:
            Union[YoutubeChannel, list[YoutubeChannel]]: The channel object containing data of the channel.

        Raises:
            HTTPException: Fetching the metadata failed.
            ChannelNotFound: The channel does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api("channels", "id", channel_id,
                                    ["snippet", "status", "contentDetails", "statistics", "topicDetails",
                                     "brandingSettings", "contentOwnerDetails", "id", "localizations"], YoutubeChannel,
                                    ChannelNotFound, 50)

    async def fetch_video_comments(self, video_id: str, max_comments: Optional[int] = 50) -> list[YoutubeCommentThread]:
        """Fetches comments on a video.

        A list of comment threads are fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeCommentThread` object.

        Args:
            video_id (str): The id of the video to use.
            max_comments (int): The maximum number of comments to fetch. Specify ``None`` to fetch all comments.
                WARNING! specifying a high number or ``None`` could hammer the api too much causing you
                to get rate limited so do this with caution.

        Returns:
            list[YoutubeCommentThread]: A list of comments as :class:`YoutubeCommentThread`.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video to look for comments on does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api("commentThreads", "videoId", video_id,
                                    ["snippet", "replies", "id"], YoutubeCommentThread,
                                    VideoNotFound, 50, max_comments, True)

    async def fetch_channel_comments(self, channel_id: str, max_comments: Optional[int] = 50
                                     ) -> list[YoutubeCommentThread]:
        """Fetches comments on an entire channel.

        A list of comment threads are fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeCommentThread` object.

        Args:
            channel_id (str): The id of the channel to use.
            max_comments (int): The maximum number of comments to fetch. Specify ``None`` to fetch all comments.
                WARNING! specifying a high number or ``None`` could hammer the api too much causing you
                to get rate limited so do this with caution.

        Returns:
            list[YoutubeCommentThread]: A list of comments as :class:`YoutubeCommentThread`.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The channel to look for comments on does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api("commentThreads", "allThreadsRelatedToChannelId", channel_id,
                                    ["snippet", "replies", "id"], YoutubeCommentThread,
                                    ChannelNotFound, 50, max_comments, True)

    async def fetch_comment(self, comment_id: Union[str, list[str]]) -> Union[YoutubeComment, list[YoutubeComment]]:
        """Fetches individual comments.

        comments are fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeComment` object or a list if a list of ids were specified.

        Args:
            comment_id (str): The id of the comment to use.

        Returns:
            Union[YoutubeComment, list[YoutubeComment]]: The YouTube comment object.

        Raises:
            HTTPException: Fetching the metadata failed.
            CommentNotFound: The comment does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a comment id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api("comments", "id", comment_id, ["snippet", "id"], YoutubeComment, CommentNotFound)

    async def fetch_comment_replies(self, comment_id: str, max_comments: Optional[int] = 50) -> list[YoutubeComment]:
        """Fetches a list of replies on a comment.

        comments are fetched using a GET request which the response is then concentrated into a
        :class:`list[YoutubeComment]` object.

        Args:
            comment_id (str): The id of the comment to use.
            max_comments (int): The maximum number of comments to fetch. Specify ``None`` to fetch all comments.
                WARNING! specifying a high number or ``None`` could hammer the api too much causing you
                to get rate limited so do this with caution.

        Returns:
            list[YoutubeComment]: The replies on the comment.

        Raises:
            HTTPException: Fetching the metadata failed.
            CommentNotFound: The comment does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a comment id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api("comments", "parentId", comment_id,
                                    ["snippet", "id"], YoutubeComment,
                                    CommentNotFound, None, max_comments, True)

    async def search(self, query: str, max_results=10, search_filter: SearchFilter = None) -> list[YoutubeSearchResult]:
        """Sends a search request to the api and returns a list of videos and/or channels and/or playlists depending
        on the query provided and the filters used.

        Args:
            query (str): The keywords to search for
            max_results (int): The maximum number of results to fetch. Defaults to 10
            search_filter (Optional[SearchFilter]): An object containing the filters active in the search

        Returns:
            list[YoutubeSearchResult]: A list of videos/channels/playlists returned by the search.

        Raises:
            HTTPException: Requesting the search failed. A 400 error is most likely due to invalid filters,
                see https://developers.google.com/youtube/v3/docs/search/list for correct usage.
            ResourceNotFound: Something went wrong while initiating the search.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The query is empty.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        def process_filters(obj: Any):
            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y-%m-%dT%H:%M:%SZ")
            elif isinstance(obj, int):
                return datetime.datetime.fromtimestamp(obj).strftime("%Y-%m-%dT%H:%M:%SZ")
            elif obj in [value[1] for value in REFERENCE_TABLE.values()]:
                return [key for key, value in REFERENCE_TABLE.items() if value[1] == obj][0]
            else:
                return snake_to_camel(str(obj))
        active_filters = None
        if search_filter is not None:
            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            active_filters = [f"{snake_to_camel(key)}={process_filters(value)}" for key, value in
                              search_filter.__dict__.items() if value is not None]
        return await self._call_api("search", "q", parse.quote(query), ["snippet"], YoutubeSearchResult,
                                    ResourceNotFound, max_results if max_results < 50 else 50, max_results, True,
                                    other_queries="&"+("&".join(active_filters)))

    async def fetch_video_captions(self, video_id: str) -> list[VideoCaption]:
        """Fetches captions on a video.

        A list of available captions are fetched using a GET request which the response is then concentrated into a
        :class:`list[VideoCaptions]` object.

        Args:
            video_id (str): The id of the video to use.

        Returns:
            list[VideoCaption]: A list of captions as :class:`VideoCaption`.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video to get captions on does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api("captions", "videoId", video_id,
                                    ["snippet", "id"], VideoCaption,
                                    VideoNotFound, None, None, True)
