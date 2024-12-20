from __future__ import annotations
import asyncio
import datetime
import json
import os
import pathlib
import socket
from email.utils import parsedate_to_datetime
from typing import Optional, Union, Any, AsyncGenerator, Callable
from urllib import parse

import aiohttp
from aiohttp import TCPConnector, web
from .exceptions import PlaylistNotFound, InvalidInput, VideoNotFound, HTTPException, APITimeout, ChannelNotFound, \
    CommentNotFound, ResourceNotFound, NoAuth, VideoCategoryNotFound, NoSession
from .types import YoutubePlaylist, PlaylistItem, YoutubeVideo, YoutubeChannel, YoutubeCommentThread, \
    YoutubeComment, YoutubeSearchResult, REFERENCE_TABLE, VideoCaption, AuthorisedYoutubeVideo, YoutubeSubscription, \
    YoutubeVideoCategory, OAuth2Session, EXISTING, LocalName, YoutubeThumbnailMetadata, BaseVideo, YoutubeBanner
from .enums import OAuth2Scope, License, PrivacyStatus, CaptionFormat
from .filters import SearchFilter
from .utils import censor_key, snake_to_camel, basic_html_page, use_existing, ensure_missing_keys


class AsyncYoutubeAPI:
    """Represents the main class for running all the tools.

    .. versionadded:: 0.4.0
        Supports OAuth2 methods for running privileged api calls.

    Attributes:
        api_version (str): The API version to use. Defaults to 3.
        call_url_prefix (str): The start of the YouTube API call url to use.
        timeout (aiohttp.ClientTimeout): The timeout if the api does not respond.
        ignore_ssl (bool): Whether to ignore any verification errors with the ssl certificate.
            This is useful for using the api on a restricted network.
        quota_usage (int): The number of YouTube API quota that have units used this session.
    """
    URL_PREFIX = "https://www.googleapis.com/youtube/v{version}"

    def __init__(
            self, yt_api_key: str = None, api_version: str = '3', timeout: float = 5, ignore_ssl: bool = False,
            session: OAuth2Session = None, oauth_token: str = None, use_oauth=False
    ):
        """
        Args:
            yt_api_key (str): The API key used to access the YouTube API. to get an API key.
                See instructions here: https://developers.google.com/youtube/v3/getting-started
            api_version (str): The API version to use. Defaults to 3.
            timeout (float): The timeout if the api does not respond.
            ignore_ssl (bool): Whether to ignore any verification errors with the ssl certificate.
                This is useful for using the api on a restricted network.
            session (OAuth2Session): The OAuth2 session used for authorised requests.

                .. versionadded:: 0.4.0
            oauth_token (str): The OAuth token to used for authorised requests.

                .. versionadded:: 0.4.0
            use_oauth (bool): Whether to use the oauth token over the api key.

                .. versionadded:: 0.4.0

        Raises:
            NoAuth: no api key or OAuth2 token was provided. *Added in version 0.4.0.*
        """
        self._key = yt_api_key
        self.api_version = api_version
        self.session = session
        self._token = session.access_token if session else oauth_token
        if (not self._key) and (not self._token):
            raise NoAuth()
        self.call_url_prefix = self.URL_PREFIX.format(version=self.api_version)
        self._skeleton_url = self.call_url_prefix + "/{kind}?part={parts}{queries}"
        self._skeleton_url_with_key = self._skeleton_url + "&key=" + (self._key or "")
        self.use_oauth = use_oauth
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.ignore_ssl = ignore_ssl
        self.quota_usage = 0

    @classmethod
    def generate_url_and_socket(
            cls, client_id: str, scopes: list[OAuth2Scope] = None
    ) -> tuple[str, socket.socket]:
        """
        Sets up a consent url and a socket to use with oauth2 authentication.

        .. versionadded:: 0.4.0

        Args:
            client_id (str): The client_id to use in the consent url.
            scopes (Optional[list[OAuth2Scope]]): The list of oauth2 scopes to include in the url.
                Defaults to :func:`ayt_api.enums.OAuth2Scope.default`

        Returns:
            tuple[str, socket.socket]: The consent url and internal socket to use later with
                :func:`with_authcode_receiver`.
        Raises:
            OSError: Setting up the socket failed
        """
        scopes = scopes or OAuth2Scope.default()
        consent_url = (
            f"https://accounts.google.com/o/oauth2/auth/oauthchooseaccount?scope="
            f"{'%20'.join([str(scope.value) for scope in scopes])}"
            "&response_type=code&redirect_uri={redirect_uri}&client_id={client_id}&service=lso&o2v=1&ddm=0"
            "&flowName=GeneralOAuthFlow"
        )
        sock = socket.socket()
        sock.bind(('127.0.0.1', 0))
        sock_name = [str(component) for component in sock.getsockname()]
        return consent_url.format(redirect_uri=f"http://{':'.join(sock_name)}", client_id=client_id), sock

    @classmethod
    async def with_authcode_receiver(
            cls, oauth2_consent_url: str, sock: socket.socket, client_secret: str, api_version: str = '3',
            timeout: float = 5, ignore_ssl: bool = False
    ):
        """
        Run the AsyncYoutubeAPI session by first setting up a web server to listen for a connection after the oauth2
        consent is complete and receive the authentication code to then exchange for an oauth2 access token.

        .. versionadded:: 0.4.0

        Args:
            oauth2_consent_url (str): The oauth2 consent url containing the client id and the redirect uri
            sock (socket.socket): The socket to listen on that the redirect uri leads to
            client_secret (str): The client secret as part of OAuth client credentials created at
                https://console.cloud.google.com/apis/credentials.
            api_version (str): The API version to use. Defaults to 3.
            timeout (float): The timeout if the api does not respond.
            ignore_ssl (bool): Whether to ignore any verification errors with the ssl certificate.
                This is useful for using the api on a restricted network.
        Returns:
            AsyncYoutubeAPI: The instance of the main class that runs all the api calls
        Raises:
            RuntimeError: The request failed.
            aiohttp.ClientError: There was a problem sending the request.
            asyncio.TimeoutError: Google's OAuth servers did not respond within the timeout period set.
        """
        qq = asyncio.Queue()

        consent_url_components = parse.urlparse(oauth2_consent_url)
        consent_url_queries = parse.parse_qs(consent_url_components.query)
        for required_parameter in ["redirect_uri", "client_id"]:
            if not consent_url_queries.get(required_parameter):
                raise ValueError(f"Missing required url parameter: `{required_parameter}`")
        redirect_uri = consent_url_queries["redirect_uri"][0]
        client_id = consent_url_queries["client_id"][0]

        async def receive(request: web.Request):
            if not request.query.get("code"):
                response = web.Response(
                    text=basic_html_page("400 Bad Request", "Missing required url parameter: <code>code</code>"),
                    content_type="text/html",
                    status=400,
                )
                return response
            try:
                api = await cls.with_authorisation_code(
                    request.query.get("code"), client_id, client_secret, redirect_uri,
                    api_version, timeout, ignore_ssl
                )
            except HTTPException as e:
                return web.Response(
                    text=basic_html_page(f"{e.status} {e.response.reason}", f"{e.message}"),
                    content_type="text/html",
                    status=e.status
                )
            except asyncio.TimeoutError as e:
                await qq.put(e)
                return web.Response(
                    text=basic_html_page(
                        "504 Gateway Timeout",
                        f"<b>oauth2.googleapis.com</b> did not respond within the timeout set"
                    ),
                    content_type="text/html",
                    status=504
                )
            except aiohttp.ClientError as e:
                await qq.put(e)
                return web.Response(
                    text=basic_html_page("500 Internal Server Error", f"{type(e).__name__}: {e}"),
                    content_type="text/html",
                    status=500
                )
            except RuntimeError as e:
                await qq.put(e)
                return web.Response(
                    text=basic_html_page("502 Bad Gateway", f"{e}"),
                    content_type="text/html",
                    status=502
                )
            await qq.put(api)
            return web.Response(
                text=basic_html_page("Authorisation Code Received", "You can close this tab now"),
                content_type="text/html"
            )

        app = web.Application()
        app.router.add_route("GET", "/", receive)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.SockSite(runner, sock)
        await site.start()
        result = await qq.get()
        if isinstance(result, BaseException):
            raise result
        return result

    @classmethod
    async def with_oauth_flow_generator(
            cls, client_id: str, client_secret: str, api_version: str = '3', timeout: float = 5,
            ignore_ssl: bool = False
    ) -> AsyncGenerator[Union[str, AsyncYoutubeAPI]]:
        """

        A generator that yields an OAuth consent url, waits for authorisation,
        and automatically requests an access token before yielding a :class:`AsyncYoutubeAPI`
        object that has oauth2 credentials automatically provided.

        .. versionadded:: 0.4.0

        An example of how to use:

        .. literalinclude:: ../../../examples/oauth2-generator.py
            :lines: 6-16
            :dedent: 4

        Args:
            client_id (str): A client id as part of OAuth client credentials created at
                https://console.cloud.google.com/apis/credentials.
            client_secret (str): The client secret as part of OAuth client credentials created at
                https://console.cloud.google.com/apis/credentials.
            api_version (str): The API version to use. Defaults to 3.
            timeout (float): The timeout if the api does not respond.
            ignore_ssl (bool): Whether to ignore any verification errors with the ssl certificate.
                This is useful for using the api on a restricted network.
        Yields:
            Union[str, AsyncYoutubeAPI]: The OAuth2 consent url and then the instance of the main class that runs all
                the api calls
        Raises:
            RuntimeError: The request failed.
            aiohttp.ClientError: There was a problem sending the request.
            asyncio.TimeoutError: Google's OAuth servers did not respond within the timeout period set.
        """
        consent_url, sock = cls.generate_url_and_socket(client_id)
        yield consent_url
        yield await cls.with_authcode_receiver(consent_url, sock, client_secret, api_version, timeout, ignore_ssl)

    @classmethod
    async def with_authorisation_code(
            cls, code: str, client_id: str, client_secret: str, redirect_uri: str,
            api_version: str = '3', timeout: float = 5, ignore_ssl: bool = False,
    ):
        """
        Run the AsyncYoutubeAPI session using OAuth 2 client credentials and an authorisation code received from an
        OAuth2 consent screen.

        .. versionadded:: 0.4.0

        Args:
            code (str): The authorisation code received after completing an OAuth2 consent screen.
            client_id (str): A client id as part of OAuth client credentials created at
                https://console.cloud.google.com/apis/credentials.
            client_secret (str): The client secret as part of OAuth client credentials created at
                https://console.cloud.google.com/apis/credentials.
            redirect_uri (str): The URI that was sent after the OAuth consent screen was completed
            api_version (str): The API version to use. Defaults to 3.
            timeout (float): The timeout if the api does not respond.
            ignore_ssl (bool): Whether to ignore any verification errors with the ssl certificate.
                This is useful for using the api on a restricted network.

        Returns:
            AsyncYoutubeAPI: The instance of the main class that runs all the api calls
        Raises:
            HTTPException: The request failed.
            aiohttp.ClientError: There was a problem sending the request.
            asyncio.TimeoutError: Google's OAuth servers did not respond within the timeout period set.
        """
        async with aiohttp.ClientSession(
                connector=TCPConnector(verify_ssl=not ignore_ssl), timeout=aiohttp.ClientTimeout(total=timeout)
        ) as request_token_session:
            request_token_data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
            async with request_token_session.post(
                "https://oauth2.googleapis.com/token",
                data=json.dumps(request_token_data),
                headers={"content-type": "application/json", }
            ) as post_response:
                if post_response.ok and post_response.content_type == "application/json":
                    content = await post_response.json()
                    return cls(
                        None, api_version, timeout, ignore_ssl,
                        OAuth2Session(
                            http_date=parsedate_to_datetime(post_response.headers.get("Date")),
                            client_id=client_id, client_secret=client_secret, **content
                        )
                    )
                error_data = None
                if post_response.content_type == "application/json":
                    error_data = await post_response.json()
                if post_response.status >= 400:
                    raise HTTPException(post_response, error_data.get("error") if error_data else None, error_data)
                raise RuntimeError("Unexpected response from oauth2.googleapis.com")

    def __repr__(self):
        return (
            f"AsyncYoutubeAPI('API_KEY', '{self.api_version}', {self.timeout.total}, {self.ignore_ssl}, 'OAUTH_TOKEN',"
            f" {self.use_oauth})"
        )

    async def refresh_session(self):
        """
        Refresh the access token for the current OAuth2 Session

        .. versionadded:: 0.4.0

        Note:
            This function is for refreshing the access_token if :class:`AsyncYoutubeAPI` was initialised using one of
            the class-methods. If the class was not initialised in this way e.g. only providing an API key or just an
            OAuth2 access token by itself, running this function will raise :class:`NoSession`.

        Raises:
            NoSession: There is no OAuth2 session to refresh.
            HTTPException: The request failed.
            aiohttp.ClientError: There was a problem sending the request.
            asyncio.TimeoutError: Google's OAuth servers did not respond within the timeout period set.
        """
        if not self.session:
            raise NoSession()
        async with aiohttp.ClientSession(
                connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout
        ) as request_token_session:
            request_token_data = {
                "refresh_token": self.session.refresh_token,
                "client_id": self.session.client_id,
                "client_secret": self.session.client_secret,
                "grant_type": "refresh_token",
            }
            async with request_token_session.post(
                "https://oauth2.googleapis.com/token",
                data=json.dumps(request_token_data),
                headers={"content-type": "application/json", }
            ) as post_response:
                if post_response.ok and post_response.content_type == "application/json":
                    content = await post_response.json()
                    self.session = OAuth2Session(
                        http_date=parsedate_to_datetime(post_response.headers.get("Date")),
                        client_id=self.session.client_id, client_secret=self.session.client_secret,
                        refresh_token=self.session.refresh_token, **content
                    )
                    return
                error_data = None
                if post_response.content_type == "application/json":
                    error_data = await post_response.json()
                if post_response.status >= 400:
                    raise HTTPException(post_response, error_data.get("error") if error_data else None, error_data)
                raise RuntimeError("Unexpected response from oauth2.googleapis.com")

    async def _call_api(
            self, call_type: str, query: Optional[str], ids: Union[str, list[str], None], parts: list[str],
            return_type: Union[type, Callable], exception_type: type[ResourceNotFound], max_results: int = None,
            max_items: int = None, multi_resp=False, next_page: str = None, next_list: list[str] = None,
            current_count=0, expected_count=1, other_queries: str = None, return_args: dict = None, auth_retry=False,
            quota_rate: int = 1
    ) -> Union[Any, list]:
        """A centralised function for calling the api.

        Args:
            call_type (str): The type of request to make to the YouTube api.
            query (Optional[str]): The variable name for the ``ids`` (identifier keywords).
            ids (Union[str, list[str], None]): The identifier keywords (usually IDs to look for).
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
            return_args (dict): Extra arguments that are passed to the object passed to ``return_type``.

                .. versionadded:: 0.4.0
            auth_retry (bool): Is the function being run again with new credentials. Defaults to ``False``.

                .. versionadded:: 0.4.0

        Returns:
            Union[Any, list]: The object specified in ``return_type``.

        Raises:
            HTTPException: Fetching the request failed.
            ResourceNotFound: The requested item was not found.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The query was empty.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        # check if session has probably expired
        if self.session and self.session.is_expired() and (not auth_retry):
            await self.refresh_session()
            return await self._call_api(
                call_type, query, ids, parts, return_type, exception_type, max_results,
                max_items, multi_resp, next_page, next_list, current_count, expected_count,
                other_queries, return_args, True, quota_rate
            )
        # use OAuth token if no api key was provided
        oauth = self.use_oauth or (not self._key)
        return_args = return_args or {}
        if ids is None:
            multi = False
        else:
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
            call_url = (self._skeleton_url if oauth else self._skeleton_url_with_key).format(
                kind=call_type, parts=",".join(parts),
                queries=f"&{query}={id_object}{x_queries}{next_page_query}{max_results_query}"
            )
            try:
                headers = {}
                if oauth:
                    headers = {
                        "Authorization": f"{self.session.token_type if self.session else 'Bearer'} {self._token}"
                    }
                async with yt_api_session.get(call_url, headers=headers) as yt_api_response:
                    self.quota_usage += quota_rate
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
                        difference = list(set(ids).difference(set(returned_items))) if ids is not None else None
                        if (
                            (difference and multi) or (not multi_resp and len(items) < 1)
                                or (ids is None and len(items) < 1)
                        ):
                            raise exception_type(difference if multi else ids)
                        else:
                            if multi or multi_resp:
                                items_next_page = []
                                if res_data.get("nextPageToken") is not None:
                                    current_count += len(res_data.get("items"))
                                    if not max_items or current_count < max_items:
                                        items_next_page = await self._call_api(
                                            call_type, query, ids, parts, return_type, exception_type, max_results,
                                            max_items, multi_resp, res_data["nextPageToken"],
                                            current_count=current_count, expected_count=expected_count,
                                            return_args=return_args, quota_rate=quota_rate
                                        )
                                items_next_list = []
                                if next_list:
                                    items_next_list = await self._call_api(
                                        call_type, query, next_list, parts, return_type, exception_type, max_results,
                                        max_items, multi_resp, expected_count=expected_count,
                                        return_args=return_args, quota_rate=quota_rate
                                    )
                                items = [return_type(item, censor_key(call_url), self, **return_args) for item in items]
                                return (items + items_next_page + items_next_list)[:max_items]
                            else:
                                res_json = res_data.get("items")[0]
                                return return_type(res_json, censor_key(call_url), self, **return_args)
                    else:
                        message = f'The youtube API returned the following error code: ' \
                                  f'{yt_api_response.status}'
                        error_data = None
                        if yt_api_response.content_type == "application/json":
                            res_data = await yt_api_response.json()
                            if "error" in res_data:
                                error_data = res_data["error"]
                                error_reasons = [error.get("reason") for error in error_data["errors"] if error]
                                not_found_check = [reason for reason in error_reasons if reason.endswith("NotFound")]
                                if not_found_check:
                                    raise exception_type(ids)
                                if "authError" in error_reasons and self.session and (not auth_retry):
                                    await self.refresh_session()
                                    return await self._call_api(
                                        call_type, query, ids, parts, return_type, exception_type, max_results,
                                        max_items, multi_resp, next_page, next_list, current_count, expected_count,
                                        other_queries, return_args, True, quota_rate
                                    )
                                message = error_data.get("message")
                        raise HTTPException(yt_api_response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    async def _update_api(
            self, call_type: str, query: Optional[str], ids: Union[str, list[str], None], parts: list[str],
            return_type: Union[type, Callable], new_values: dict,
            exception_type: type[ResourceNotFound], max_results: int = None, max_items: int = None, multi_resp=False,
            next_page: str = None, next_list: list[str] = None, current_count=0, expected_count=1,
            other_queries: str = None, return_args: dict = None, auth_retry=False, quota_rate: int = 50
    ) -> Union[Any, list]:
        """A centralised function for sending update requests to the api.

        Args:
            call_type (str): The type of request to make to the YouTube api.
            query (Optional[str]): The variable name for the ``ids`` (identifier keywords).
            ids (Union[str, list[str], None]): The identifier keywords (usually IDs to look for).
            parts (list[str]): A list of parts to request of the main request.
            return_type (Union[type, Callable]): The object to return the results in.
            new_values: (dict): The editable values of the object populated with the existing ones and once to edit.
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
            return_args (dict): Extra arguments that are passed to the object passed to ``return_type``.

                .. versionadded:: 0.4.0
            auth_retry (bool): Is the function being run again with new credentials. Defaults to ``False``.

                .. versionadded:: 0.4.0

        Returns:
            Union[Any, list]: The object specified in ``return_type``.

        Raises:
            HTTPException: Fetching the request failed.
            ResourceNotFound: The requested item was not found.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The query was empty.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        # check if session has probably expired
        if self.session and self.session.is_expired() and (not auth_retry):
            await self.refresh_session()
            return await self._update_api(
                call_type, query, ids, parts, return_type, new_values, exception_type, max_results,
                max_items, multi_resp, next_page, next_list, current_count, expected_count,
                other_queries, return_args, True, quota_rate
            )
        # use OAuth token if no api key was provided
        return_args = return_args or {}
        if ids is None:
            multi = False
        else:
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
            call_url = self._skeleton_url.format(
                kind=call_type, parts=",".join(parts),
                queries=f"&{query}={id_object}{x_queries}{next_page_query}{max_results_query}"
            )
            try:
                headers = {
                    "Authorization": f"{self.session.token_type if self.session else 'Bearer'} {self._token}",
                    "content-type": "application/json"
                }
                async with yt_api_session.put(
                        call_url,
                        data=json.dumps(new_values),
                        headers=headers
                ) as yt_api_response:
                    self.quota_usage += quota_rate
                    if yt_api_response.ok:
                        res_data = await yt_api_response.json()
                        if "error" in res_data:
                            check = [error.get("reason") for error in res_data["error"]["errors"]
                                     if error.get("reason").endswith("NotFound")]
                            if check:
                                raise exception_type(ids)
                            raise HTTPException(yt_api_response, f'{res_data["error"].get("code")}: '
                                                                 f'{res_data["error"].get("message")}')
                        items = [res_data]
                        returned_items = [item.get("id") if isinstance(item.get("id"), str) else None for item in items]
                        difference = list(set(ids).difference(set(returned_items))) if ids is not None else None
                        if (
                            (difference and multi) or (not multi_resp and len(items) < 1)
                                or (ids is None and len(items) < 1)
                        ):
                            raise exception_type(difference if multi else ids)
                        else:
                            if multi or multi_resp:
                                items_next_page = []
                                if res_data.get("nextPageToken") is not None:
                                    current_count += len(res_data.get("items"))
                                    if not max_items or current_count < max_items:
                                        items_next_page = await self._update_api(
                                            call_type, query, ids, parts, return_type, new_values,
                                            exception_type, max_results, max_items, multi_resp,
                                            res_data["nextPageToken"], current_count=current_count,
                                            expected_count=expected_count, return_args=return_args,
                                            quota_rate=quota_rate
                                        )
                                items_next_list = []
                                if next_list:
                                    items_next_list = await self._update_api(
                                        call_type, query, next_list, parts, return_type, new_values,
                                        exception_type, max_results, max_items, multi_resp,
                                        expected_count=expected_count, return_args=return_args, quota_rate=quota_rate
                                    )
                                items = [
                                   return_type(
                                       item, censor_key(call_url), self, **return_args
                                   ) for item in items
                                ]
                                return (items + items_next_page + items_next_list)[:max_items]
                            else:
                                res_json = res_data
                                return return_type(res_json, censor_key(call_url), self, **return_args)
                    else:
                        message = f'The youtube API returned the following error code: ' \
                                  f'{yt_api_response.status}'
                        error_data = None
                        if yt_api_response.content_type == "application/json":
                            res_data = await yt_api_response.json()
                            if "error" in res_data:
                                error_data = res_data["error"]
                                error_reasons = [error.get("reason") for error in error_data["errors"] if error]
                                not_found_check = [reason for reason in error_reasons if reason.endswith("NotFound")]
                                if not_found_check:
                                    raise exception_type(ids)
                                if "authError" in error_reasons and self.session and (not auth_retry):
                                    await self.refresh_session()
                                    return await self._update_api(
                                        call_type, query, ids, parts, return_type, new_values,
                                        exception_type, max_results, max_items, multi_resp, next_page, next_list,
                                        current_count, expected_count, other_queries, return_args, True, quota_rate
                                    )
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

    async def save_thumbnail(self, thumbnail_url: str, fp: Union[os.PathLike, str, None] = None):
        """Downloads the thumbnail specified and saves it to a specified location

        Args:
            thumbnail_url (str): The i.ytimg.com asset url of the thumbnail
            fp (Union[os.PathLike, str, None]): The path and/or filename to save the file to.
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
            banner_url (str): The yt3.ggpht.com or yt3.googleusercontent.com asset url of the banner

        Returns:
            tuple[bytes, str]: A list containing the image as a :class:`bytes` object and the file extension of
                the image

        Raises:
            HTTPException: Fetching the request failed.
            aiohttp.ClientError: There was a problem sending the request to the server.
            asyncio.TimeoutError: The yt3.ggpht.com or yt3.googleusercontent.com server did not respond within the
                timeout period set.
        """
        async with (aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout)
                    as thumbnail_session):
            async with thumbnail_session.get(banner_url) as thumbnail_response:
                if not thumbnail_response.ok:
                    raise HTTPException(thumbnail_response)
                else:
                    return await thumbnail_response.read(), thumbnail_response.content_type.split("/")[-1]

    async def save_banner(self, banner_url: str, fp: Union[os.PathLike, str, None] = None):
        """Downloads the banner specified and saves it to a specified location

        Args:
            banner_url (str): The yt3.ggpht.com or yt3.googleusercontent.com asset url of the thumbnail
            fp (Union[os.PathLike, str, None]): The path and/or filename to save the file to.
                Defaults to current working directory with the filename format: ``{banner_id}.{extension}``

        Raises:
            HTTPException: Fetching the request failed.
            aiohttp.ClientError: There was a problem sending the request to the server.
            asyncio.TimeoutError: The yt3.ggpht.com or yt3.googleusercontent.com server did not respond within the
                timeout period set.
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

    async def download_caption(
            self, track_id: str, track_format: Optional[CaptionFormat] = None, language: Optional[str] = None,
            _auth_retry=False
    ) -> bytes:
        """Downloads the caption track from the ID specified and stores it as a :class:`bytes` object

        .. versionadded:: 0.4.0

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **200** units per call.

        Note:
            You must be the owner of the video of the captions and use OAuth authentication to call this method with
            one of the following scopes:

            - :class:`ayt_api.enums.OAuth2Scope.youtube_force_ssl`
            - :class:`ayt_api.enums.OAuth2Scope.youtube_partner`

        Args:
            track_id (str): The ID of the caption track
            track_format (Optional[CaptionFormat]): The format YouTube should return the captions in.
            language (Optional[str]): The alpha-2 language code to translate the caption track into.
            _auth_retry (bool): Is the function being run again with new credentials. Defaults to ``False``.

        Returns:
            bytes: The caption track as a :class:`bytes` object.

        Raises:
            HTTPException: Fetching the request failed.
            aiohttp.ClientError: There was a problem sending the request to the api.
            asyncio.TimeoutError: The API server did not respond within the timeout period set.
        """
        if self.session and self.session.is_expired() and (not _auth_retry):
            await self.refresh_session()
            return await self.download_caption(track_id, track_format, language, True)
        queries = []
        if track_format:
            queries.append(f"tfmt={track_format.__str__()}")
        if language:
            queries.append(f"tlang={language}")
        url = (
            self.call_url_prefix + "/captions/" + track_id +
            (("?" + "&".join(queries)) if queries else "")
        )
        async with (aiohttp.ClientSession(connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout)
                    as thumbnail_session):
            headers = {
                "Authorization": f"{self.session.token_type if self.session else 'Bearer'} {self._token}"
            }
            async with thumbnail_session.get(url, headers=headers) as thumbnail_response:
                self.quota_usage += 200
                if not thumbnail_response.ok:
                    message = f'The youtube API returned the following error code: ' \
                              f'{thumbnail_response.status}'
                    error_data = None
                    if thumbnail_response.content_type == "application/json":
                        res_data = await thumbnail_response.json()
                        if "error" in res_data:
                            error_data = res_data["error"]
                            error_reasons = [error.get("reason") for error in error_data["errors"] if error]
                            if "authError" in error_reasons and self.session and (not _auth_retry):
                                await self.refresh_session()
                                return await self.download_caption(track_id, track_format, language, True)
                            message = error_data.get("message")
                    raise HTTPException(thumbnail_response, message, error_data)
                else:
                    return await thumbnail_response.read()

    async def save_caption(
            self, track_id: str, *, track_format: Optional[CaptionFormat] = None, language: Optional[str] = None,
            fp: Union[os.PathLike, str, None] = None
    ):
        """Downloads the caption track from the ID specified and saves it to a specified location

        .. versionadded:: 0.4.0

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **200** units per call.

        Note:
            You must be the owner of the video of the captions and use OAuth authentication to call this method with
            one of the following scopes:

            - :class:`ayt_api.enums.OAuth2Scope.youtube_force_ssl`
            - :class:`ayt_api.enums.OAuth2Scope.youtube_partner`

        Args:
            track_id (str): The ID of the caption track
            track_format (Optional[CaptionFormat]): The format YouTube should return the captions in.
            language (Optional[str]): The alpha-2 language code to translate the caption track into.
            fp (Union[os.PathLike, str, None]): The path and/or filename to save the file to.
                Defaults to current working directory with the filename format: ``{track_id}.{file_extension (if any)}``

        Raises:
            HTTPException: Fetching the request failed.
            aiohttp.ClientError: There was a problem sending the request to the api.
            asyncio.TimeoutError: The API did not respond within the timeout period set.
        """
        caption_track = await self.download_caption(track_id, track_format, language)
        default_filename = (
                track_id + (f"-{language}" if language else "") +
                (f".{track_format.__str__()}" if track_format else "")
        )
        if isinstance(fp, str):
            fp = pathlib.Path(fp)
        path = (fp or pathlib.Path(default_filename)).expanduser()
        if path.is_dir():
            path = path.joinpath(default_filename)
        with open(path, "wb") as thumbnail_file:
            thumbnail_file.write(caption_track)

    async def fetch_playlist(self, playlist_id: Union[str, list[str]]) -> Union[YoutubePlaylist, list[YoutubePlaylist]]:
        """Fetches playlist metadata using a playlist id.

        Playlist metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubePlaylist` object.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 playlists fetched**.

        Args:
            playlist_id (str): The id of the playlist to use. e.g. ``PLwZcI0zn-Jhc-H2CQvoqKvPuC8C9gClIF``.

        Returns:
            Union[YoutubePlaylist, list[YoutubePlaylist]]: The playlist object containing data of the playlist.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api(
            "playlists", "id", playlist_id, ["snippet", "status", "contentDetails", "player", "localizations"],
            YoutubePlaylist, PlaylistNotFound
        )

    async def fetch_playlist_items(self, playlist_id: str, max_items=None) -> list[PlaylistItem]:
        """Fetches a list of items in a playlist using a playlist id.

        Playlist video metadata is fetched using a GET request which the response is then concentrated into a list of
        :class:`PlaylistItem` objects.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 items fetched**.

        Args:
            playlist_id (str): The id of the playlist to use. e.g. ``PLwZcI0zn-Jhc-H2CQvoqKvPuC8C9gClIF``.
            max_items (int | None): The maximum number of playlist items to fetch. Defaults to ``None`` which
                fetches every item in a playlist.

                .. versionadded:: 0.4.0

                Warning:
                    If a specified playlist has a lot of videos, not specifying a value to ``max_items`` could
                    hammer the api too much causing you to get rate limited so do this with caution.

        Returns:
            list[PlaylistItem]: A list containing playlist video objects.

        Raises:
            HTTPException: Fetching the metadata failed.
            PlaylistNotFound: The playlist does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a playlist id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api(
            "playlistItems", "playlistId", playlist_id, ["snippet", "status", "contentDetails"],
            PlaylistItem, PlaylistNotFound, 500, max_items, True
        )

    async def fetch_playlist_videos(self, playlist_id, exclude: list[str] = None) -> list[YoutubeVideo]:
        """Fetches a list of videos in a playlist using a playlist id.

        Playlist videos are fetched using a GET request which the response is then concentrated into a list of
        :class:`YoutubeVideo` objects.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **2** units per call or **per 50 videos fetched**.

        Args:
            playlist_id (str): The id of the playlist to use. e.g. ``PLwZcI0zn-Jhc-H2CQvoqKvPuC8C9gClIF``.
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

    async def fetch_video(
            self, video_id: Union[str, list[str]], authorised=False
    ) -> Union[YoutubeVideo, list[YoutubeVideo], AuthorisedYoutubeVideo, list[AuthorisedYoutubeVideo]]:
        """Fetches information on a video using a video id.

        Video metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeVideo` object if one ID was specified if more, it returns a list of them.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 videos fetched**.

        Args:
            video_id (str): The id of the video to use. e.g. ``dQw4w9WgXcQ``. Look familiar?
            authorised (bool): Whether to fetch additional uploader side information about a video
                (Needs OAuth token).

                .. versionadded:: 0.4.0

        Returns:
            Union[YoutubeVideo, list[YoutubeVideo], AuthorisedYoutubeVideo, list[AuthorisedYoutubeVideo]]:
                The video object containing data of the video.

                .. versionchanged:: 0.4.0
                    Now could also return a :class:`AuthorisedYoutubeVideo` as well

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api(
            "videos", "id", video_id,
            [
                "snippet", "status", "contentDetails", "statistics", "player", "topicDetails",
                "recordingDetails", "liveStreamingDetails", "localizations", "paidProductPlacementDetails"
            ] + (["fileDetails", "processingDetails", "suggestions",] if authorised else []),
            AuthorisedYoutubeVideo if authorised else YoutubeVideo, VideoNotFound, 50,
        )

    async def fetch_channel(
            self, channel_id: Union[str, list[str]], authorised=False
    ) -> Union[YoutubeChannel, list[YoutubeChannel]]:
        """Fetches information on a channel using a channel id.

        Channel metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeChannel` object or a list if multiple IDs were specified.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 channels fetched**.

        Args:
            channel_id (str): The id of the channel to use. e.g. ``UC1VSDiiRQZRTbxNvWhIrJfw``.
            authorised (bool): Whether to fetch additional owner side information about a channel e.g. audit details
                (Needs OAuth token).

                .. versionadded:: 0.4.0

        Returns:
            Union[YoutubeChannel, list[YoutubeChannel]]: The channel object containing data of the channel.

        Raises:
            HTTPException: Fetching the metadata failed.
            ChannelNotFound: The channel does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api(
            "channels", "id", channel_id,
            [
                "snippet", "status", "contentDetails", "statistics", "topicDetails",
                "brandingSettings", "contentOwnerDetails", "id", "localizations"
            ] + (["auditDetails"] if authorised else []),
            YoutubeChannel, ChannelNotFound, 50
        )

    async def fetch_channel_from_handle(
            self, handle: Union[str, list[str]], authorised=False
    ) -> Union[YoutubeChannel, list[YoutubeChannel]]:
        """Fetches information on a channel using a channel's handle.

        Channel metadata is fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeChannel` object or a list if multiple IDs were specified.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 channels fetched**.

        .. versionadded:: 0.4.0

        Args:
            handle (str): The handle of the channel to use. e.g. **@Revnoplex**.
            authorised (bool): Whether to fetch additional owner side information about a channel e.g. audit details
                (Needs OAuth token).

                .. versionadded:: 0.4.0

        Returns:
            Union[YoutubeChannel, list[YoutubeChannel]]: The channel object containing data of the channel.

        Raises:
            HTTPException: Fetching the metadata failed.
            ChannelNotFound: The channel does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel handle.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api(
            "channels", "forHandle", handle,
            [
                "snippet", "status", "contentDetails", "statistics", "topicDetails",
                "brandingSettings", "contentOwnerDetails", "id", "localizations"
             ] + (["auditDetails"] if authorised else []),
            YoutubeChannel, ChannelNotFound, 50
        )

    async def fetch_video_comments(self, video_id: str, max_comments: Optional[int] = 50) -> list[YoutubeCommentThread]:
        """Fetches comments on a video.

        A list of comment threads are fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeCommentThread` object.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 comments fetched**.

        Args:
            video_id (str): The id of the video to use. e.g. ``dQw4w9WgXcQ``. Look familiar?
            max_comments (int): The maximum number of comments to fetch. Specify ``None`` to fetch all comments.

                Warning:
                    Specifying a high number or ``None`` could hammer the api too much causing you to get rate limited
                    so do this with caution.

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

    async def fetch_channel_comments(
            self, channel_id: str, max_comments: Optional[int] = 50
    ) -> list[YoutubeCommentThread]:
        """Fetches comments on an entire channel.

        A list of comment threads are fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeCommentThread` object.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 comments fetched**.

        Args:
            channel_id (str): The id of the channel to use. e.g. ``UC1VSDiiRQZRTbxNvWhIrJfw``.
            max_comments (int): The maximum number of comments to fetch. Specify ``None`` to fetch all comments.

                Warning:
                    Specifying a high number or ``None`` could hammer the api too much causing you to get rate limited
                    so do this with caution.

        Returns:
            list[YoutubeCommentThread]: A list of comments as :class:`YoutubeCommentThread`.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The channel to look for comments on does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api(
            "commentThreads", "allThreadsRelatedToChannelId", channel_id, ["snippet", "replies", "id"],
            YoutubeCommentThread, ChannelNotFound, 50, max_comments, True
        )

    async def fetch_comment(self, comment_id: Union[str, list[str]]) -> Union[YoutubeComment, list[YoutubeComment]]:
        """Fetches individual comments.

        comments are fetched using a GET request which the response is then concentrated into a
        :class:`YoutubeComment` object or a list if a list of ids were specified.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 comments fetched**.

        Args:
            comment_id (str): The id of the comment to use. e.g. ``UgzuC3zzpRZkjc5Qzsd4AaABAg``.

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

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 comments fetched**.

        Args:
            comment_id (str): The id of the comment to use. e.g. ``UgzuC3zzpRZkjc5Qzsd4AaABAg``.
            max_comments (int): The maximum number of comments to fetch. Specify ``None`` to fetch all comments.

                Warning:
                    Specifying a high number or ``None`` could hammer the api too much causing you to get rate limited
                    so do this with caution.

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

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **100** units per call or **per 50 results fetched**.

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
        return await self._call_api(
            "search", "q", parse.quote(query), ["snippet"], YoutubeSearchResult, ResourceNotFound,
            max_results if max_results < 50 else 50, max_results, True, other_queries="&"+("&".join(active_filters)),
            quota_rate=100
        )

    async def fetch_video_captions(self, video_id: str) -> list[VideoCaption]:
        """Fetches captions on a video.

        A list of available captions are fetched using a GET request which the response is then concentrated into a
        :class:`list[VideoCaptions]` object.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **50** units per call or **per 50 captions fetched**.

        Args:
            video_id (str): The id of the video to use. e.g. ``dQw4w9WgXcQ``. Look familiar?

        Returns:
            list[VideoCaption]: A list of captions as :class:`VideoCaption`.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video to get captions on does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api(
            "captions", "videoId", video_id, ["snippet", "id"], VideoCaption, VideoNotFound, None, None, True,
            quota_rate=50
        )

    async def resolve_handle(self, username: str) -> str:
        """
        Resolve a channel's handle name into a channel id.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call.

        .. versionadded:: 0.4.0

        Args:
            username (str): The handle name of the channel to resolve. e.g. **@Revnoplex**.

        Returns:
            str: The ID of the channel. e.g. ``UC1VSDiiRQZRTbxNvWhIrJfw``.

        Raises:
            HTTPException: Resolving the channel handle failed.
            ChannelNotFound: The given handle didn't match any channels.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a handle.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return (await self._call_api(
            "channels", "forHandle", username, ["id"], YoutubeChannel, ChannelNotFound,
            return_args={"partial": True},
        )).id

    async def fetch_subscriptions(self, channel_id: str, max_items: int = 50) -> list[YoutubeSubscription]:
        """
        Fetch subscriptions a specified channel has

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 subscriptions fetched**.

        .. versionadded:: 0.4.0

        Args:
            channel_id (str): The ID of the channel to fetch the subscriptions of. e.g. ``UC1VSDiiRQZRTbxNvWhIrJfw``.
            max_items (int): The maximum number of subscriptions to fetch. Defaults to 50. Specify ``None`` to fetch
                all comments.

                Warning:
                    Specifying a high number or ``None`` could hammer the api too much causing you
                    to get rate limited so do this with caution.

        Returns:
            list[YoutubeSubscription]: A list of the channel's subscriptions as :class:`YoutubeSubscription`

        Raises:
            HTTPException: Fetching the subscriptions failed.
            ChannelNotFound: The channel to get subscriptions on does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a channel id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api(
            "subscriptions", "channelId", channel_id, ["contentDetails", "snippet", "subscriberSnippet"],
            YoutubeSubscription, ChannelNotFound, max_items if max_items < 50 else 50, max_items, True
        )

    async def fetch_video_category(
            self, category_id: Union[str, list[str]]
    ) -> Union[YoutubeVideoCategory, list[YoutubeVideoCategory]]:
        """
        Fetches a category that has been or could be associated with uploaded videos.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 categories fetched**.

        .. versionadded:: 0.4.0

        Args:
            category_id (Union[str, list[str]]): The video category ID/s to fetch

        Returns:
            Union[YoutubeVideoCategory, list[YoutubeVideoCategory]]: The video category/ies

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoCategoryNotFound: The video category does not exist.
            aiohttp.ClientError: There was a problem sending the request to the api.
            InvalidInput: The input is not a video category id.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        return await self._call_api(
            "videoCategories", "id", category_id, ["snippet"], YoutubeVideoCategory, VideoCategoryNotFound, 50
        )

    async def fetch_youtube_regions(self, language: str = None) -> dict[str, str]:
        """
        Fetches a dictionary containing the names of regions listed by YouTube

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 regions fetched**.

        .. versionadded:: 0.4.0

        Args:
            language (str): The BCP-47 language code to return the results in

        Returns:
            dict[str, str]: A dictionary containing ISO 3166-1 alpha-2 codes mapped to their names listed by YouTube
        Raises:
            HTTPException: Fetching the metadata failed.
            ResourceNotFound: No region codes could be found for the specified language.
            aiohttp.ClientError: There was a problem sending the request to the api.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        to_parse = await self._call_api(
            "i18nRegions", "hl" if language else None, language, ["snippet"],
            lambda metadata, _, _2: metadata["snippet"], ResourceNotFound, 50, multi_resp=True
        )
        return {entry["gl"]: entry["name"] for entry in to_parse}

    async def fetch_youtube_languages(self, language: str) -> dict[str, str]:
        """
        Fetches a dictionary containing the names of languages listed by YouTube

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **1** unit per call or **per 50 languages fetched**.

        .. versionadded:: 0.4.0

        Args:
            language (str): The BCP-47 language code to return the results in

        Returns:
            dict[str, str]: A dictionary containing BCP-47 language codes mapped to their names listed by YouTube
        Raises:
            HTTPException: Fetching the metadata failed.
            ResourceNotFound: No region codes could be found for the specified language.
            aiohttp.ClientError: There was a problem sending the request to the api.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        to_parse = await self._call_api(
            "i18nLanguages", "hl" if language else None, language, ["snippet"],
            lambda metadata, _, _2: metadata["snippet"], ResourceNotFound, 50, multi_resp=True
        )
        return {entry["hl"]: entry["name"] for entry in to_parse}

    # The following noinspection is to stop a false warning caused by the syntax of the notes.
    # noinspection PyIncorrectDocstring
    async def update_video(
            self, video: Union[AuthorisedYoutubeVideo, list[AuthorisedYoutubeVideo]], *,
            title: Union[str, EXISTING] = EXISTING,
            category_id: Union[str, EXISTING] = EXISTING,
            default_language: Union[str, EXISTING, None] = EXISTING,
            description: Union[str, EXISTING, None] = EXISTING,
            tags: Union[list[str], EXISTING, None] = EXISTING,
            embeddable: Union[bool, EXISTING, None] = EXISTING,
            video_license: Union[License, EXISTING, None] = EXISTING,
            visibility: Union[PrivacyStatus, EXISTING, None] = EXISTING,
            public_stats_viewable: Union[bool, EXISTING, None] = EXISTING,
            publish_at: Union[datetime.datetime, EXISTING, None] = EXISTING,
            made_for_kids: Union[bool, EXISTING, None] = EXISTING,
            contains_synthetic_media: Union[bool, EXISTING, None] = EXISTING,
            recording_date: Union[datetime.datetime, EXISTING, None] = EXISTING,
            localisations: Union[list[LocalName], EXISTING, None] = EXISTING

    ) -> Union[AuthorisedYoutubeVideo, list[AuthorisedYoutubeVideo]]:
        """Updates metadata for a video.

        .. versionadded:: 0.4.0

        Values default to a special constant called ``EXISTING`` which is from the class
        :class:`ayt_api.types.UseExisting`. Specify any other value in order to edit the property you want.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **50** units per call.

        Important:
            Specifying ``None`` for a parameter will wipe it or set it to YouTube's default value.

        Args:
            video (Union[YoutubeVideo, list[YoutubeVideo]]): The YouTube video instance to be updated.
            title (Union[str, EXISTING]): The title of the video to set.

                Note:
                    This value cannot be set to ``None`` or an empty string as YouTube forbids this.

            category_id (Union[str, EXISTING]): The category id to set for the video.

                Note:
                    This value cannot be set to ``None`` or an empty string as YouTube forbids this.

            default_language (Union[str, EXISTING, None]): The default language the video should be set in.
                The value should be a BCP-47 language code.
            description (Union[str, EXISTING, None]): The description of the video to set.
            tags (Union[list[str], EXISTING, None]): The tags the to set to make the video appear in search results
                relating to it.
            embeddable (Union[bool, EXISTING, None]): Set whether the video can be embedded on another
                website.
            video_license (Union[License, EXISTING, None]): The YouTube license to set for the video.
            visibility (Union[PrivacyStatus, EXISTING, None]): Set the video's privacy status.
            public_stats_viewable (Union[bool, EXISTING, None]): Set whether the extended video statistics on the
                video's watch page are publicly viewable.
            publish_at (Union[datetime.datetime, EXISTING, None]): Set the date and time when the video is scheduled to
                publish.

                Note:
                    If you set a value for this property, you must also set the ``visibility`` property to
                    :class:`ayt_api.enums.PrivacyStatus.private`.

            made_for_kids (Union[bool, EXISTING, None]): Designate the video as being child-directed.
            contains_synthetic_media (Union[bool, EXISTING, None]): Tell YouTube if the video contain realistic
                Altered or Synthetic (A/S) content.
            recording_date (Union[datetime.datetime, EXISTING, None]): Set the date and time when the video was
                recorded.
            localisations (Union[list[LocalName], EXISTING, None]): Specify translations of the video's metadata.

        Returns:
            Union[AuthorisedYoutubeVideo, list[AuthorisedYoutubeVideo]]:
                The updated video object.

        Raises:
            HTTPException: Fetching the metadata failed.
            VideoNotFound: The video does not exist.
            aiohttp.ClientError: There was a problem sending the request to the API.
            InvalidInput: The input is not a video ID.
            APITimeout: The YouTube API did not respond within the timeout period set.
        """
        edit_mapping = {
            "id": video.id,
            "snippet": {
                "title": title or video.title,
                "categoryId": category_id or video.category_id,
                "defaultLanguage": use_existing(video.default_language, default_language),
                "description": use_existing(video.description, description),
                "tags": use_existing(video.tags, tags),
            },
            "status": {
                "embeddable": use_existing(video.embeddable, embeddable),
                "license": use_existing(
                    snake_to_camel(video.license.__str__()) if video.license else None,
                    snake_to_camel(video_license.__str__()) if video_license else video_license
                ),
                "privacyStatus": use_existing(
                    snake_to_camel(video.visibility.__str__()),
                    snake_to_camel(visibility.__str__()) if visibility else visibility
                ),
                "publicStatsViewable": use_existing(video.public_stats_viewable, public_stats_viewable),
                "publishAt": use_existing(
                    video.publish_set_at.isoformat() if video.publish_set_at else None,
                    publish_at.isoformat() if publish_at else publish_at
                ),
                "selfDeclaredMadeForKids": use_existing(video.self_declared_made_for_kids, made_for_kids),
                "containsSyntheticMedia": use_existing(video.contains_synthetic_media, contains_synthetic_media)
            },
            "recordingDetails": {
                "recordingDate": use_existing(
                    video.recording_details.date.isoformat() if video.recording_details.date else None,
                    recording_date.isoformat() if recording_date else recording_date
                )
            },
            "localizations": {
                local_name.language: {
                    "title": local_name.title,
                    "description": local_name.description
                } for local_name in use_existing(video.localisations, localisations) if local_name.language
            } if use_existing(video.localisations, localisations) else {}
        }
        updated_metadata = video.metadata.copy()
        updated_metadata.update(edit_mapping)
        return await self._update_api(
            "videos", "id", video.id,
            [
                "snippet", "status", "contentDetails", "statistics", "player", "topicDetails",
                "recordingDetails", "liveStreamingDetails", "localizations", "paidProductPlacementDetails",
                "fileDetails", "processingDetails", "suggestions", "id"],
            AuthorisedYoutubeVideo, updated_metadata, VideoNotFound, None,
        )

    async def set_video_thumbnail(self, video_id: str, image: bytes, _auth_retry=False) -> YoutubeThumbnailMetadata:
        """
        Upload and set the thumbnail for a video.

        .. versionadded:: 0.4.0

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **50** units per call.

        Args:
            video_id (str): The ID of the video to set the thumbnail of.
            image (bytes): The thumbnail image to upload.
            _auth_retry (bool): Is the function being run again with new credentials. Defaults to ``False``.

        Returns:
            YoutubeThumbnailMetadata: The metadata of the uploaded thumbnail.

        Raises:
            HTTPException: Uploading the thumbnail failed.
            ResourceNotFound: The API didn't return any thumbnail metadata.
            aiohttp.ClientError: There was a problem sending the request to the API.
            APITimeout: The YouTube api did not respond within the timeout period set.
        """
        if self.session and self.session.is_expired() and (not _auth_retry):
            await self.refresh_session()
            return await self.set_video_thumbnail(video_id, image, True)
        supported_formats = {
            "png": b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',
            "jpeg": b'\xFF\xD8\xFF'
        }
        content_type = "application/octet-stream"
        for format_name, signature in supported_formats.items():
            if image.startswith(signature):
                content_type = f"image/{format_name}"
        async with aiohttp.ClientSession(
                connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout
        ) as session:
            headers = {
                "Authorization": f"{self.session.token_type if self.session else 'Bearer'} {self._token}",
                "Content-Type": content_type,
                "Content-Length": str(len(image))
            }
            try:
                async with session.post(
                    f"https://www.googleapis.com/upload/youtube/v{self.api_version}/thumbnails/set"
                    f"?videoId={video_id}&uploadType=media", headers=headers, data=image
                ) as response:
                    self.quota_usage += 50
                    if response.ok:
                        res_data = await response.json()
                        if "error" in res_data:
                            raise HTTPException(
                                response, f'{res_data["error"].get("code")}: {res_data["error"].get("message")}')
                        items = res_data.get("items") or []
                        if not items:
                            raise ResourceNotFound("The API didn't return any thumbnail metadata")
                        else:
                            return YoutubeThumbnailMetadata(items[0], self, res_data.get("etag"))
                    else:
                        message = f'The youtube API returned the following error code: ' \
                                  f'{response.status}'
                        error_data = None
                        if response.content_type == "application/json":
                            res_data = await response.json()
                            if "error" in res_data:
                                error_data = res_data["error"]
                                error_reasons = [error.get("reason") for error in error_data["errors"] if error]
                                if "authError" in error_reasons and self.session and (not _auth_retry):
                                    await self.refresh_session()
                                    return await self.set_video_thumbnail(video_id, image, True)
                                message = error_data.get("message")
                        raise HTTPException(response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)

    # the noinspection is for the same issue as update_video()
    # noinspection PyIncorrectDocstring
    async def update_channel(
            self, channel: Union[YoutubeChannel, list[YoutubeChannel]], *,
            country: Union[str, EXISTING, None] = EXISTING,
            description: Union[str, EXISTING, None] = EXISTING,
            default_language: Union[str, EXISTING, None] = EXISTING,
            keywords: Union[list[str], EXISTING, None] = EXISTING,
            tracking_analytics_account_id: Union[str, EXISTING, None] = EXISTING,
            unsubscribed_trailer: Union[str, BaseVideo, EXISTING, None] = EXISTING,
            localisations: Union[list[LocalName], EXISTING, None] = EXISTING,
            made_for_kids: Union[bool, EXISTING] = EXISTING

    ) -> Union[YoutubeChannel, list[YoutubeChannel]]:
        """Updates metadata for a channel.

        .. versionadded:: 0.4.0

        Values default to a special constant called ``EXISTING`` which is from the class
        :class:`ayt_api.types.UseExisting`. Specify any other value in order to edit the property you want.

        .. admonition:: Quota Impact

            A call to this method has a quota cost of between **0-150** units.
            As updating ``localisations`` and ``made_for_kids`` cost an extra 50 units each
            and not updating anything costs nothing as no API call is actually made.

        Note:
            If no arguments after ``channel`` are specified or are all set to ``EXISTING``, no API call is made and
            hence no quota units will be used. The function will just return the :class:`YoutubeChannel` as it is.

        Important:
            Specifying ``None`` for a parameter will wipe it or set it to YouTube's default value.

        Args:
            channel (Union[YoutubeVideo, list[YoutubeVideo]]): The YouTube channel instance to be updated.
            country (Union[str, EXISTING, None]): The country to set which the channel is associated.
            description (Union[str, EXISTING, None]): The description of the channel to set.
            default_language (Union[str, EXISTING, None]): The default language the video should be set in.
                The value should be a BCP-47 language code.
            keywords (Union[list[str], EXISTING, None]): Keywords to set associated with your channel.
            tracking_analytics_account_id (Union[str, EXISTING, None]): The ID to set for a Google Analytics account
                used to track and measure traffic to the channel.
            unsubscribed_trailer (Union[str, BaseVideo, EXISTING, None]): The ID or :class:`BaseVideo` to set of the
                video that should play in the featured video module in the channel page's browse view for unsubscribed
                viewers.
            localisations (Union[list[LocalName], EXISTING, None]): Specify translations of the video's metadata.

                Note:
                    This value cannot be set to ``None`` or an empty list as YouTube forbids this.

            made_for_kids (Union[bool, EXISTING]): Designate the channel as being child-directed.

                Note:
                    This value cannot be set to ``None`` as YouTube forbids this.


        Returns:
            Union[YoutubeChannel, list[YoutubeChannel]]:
                The updated channel object.

        Raises:
            HTTPException: Fetching the metadata failed.
            ChannelNotFound: The channel does not exist.
            aiohttp.ClientError: There was a problem sending the request to the API.
            InvalidInput: The input is not a channel ID.
            APITimeout: The YouTube API did not respond within the timeout period set.
        """
        branding_settings_mapping = [
            {
                "id": channel.id,
                "brandingSettings": {"channel": {
                    "country": use_existing(channel.country, country),
                    "description": use_existing(channel.description, description),
                    "defaultLanguage": use_existing(channel.default_language, default_language),
                    "keywords": " ".join(
                        [
                            f"\"{keyword}\"" if " " in keyword else keyword
                            for keyword in use_existing(channel.keywords, keywords) or []
                        ]
                    ),
                    "trackingAnalyticsAccountId": use_existing(
                        channel.tracking_analytics_account_id, tracking_analytics_account_id
                    ),
                    "unsubscribedTrailer": use_existing(
                        channel.unsubscribed_trailer_id,
                        unsubscribed_trailer.id if isinstance(unsubscribed_trailer, BaseVideo) else unsubscribed_trailer
                    )
                }}
            },
        ]
        made_for_kids_mapping = [
            {
                "id": channel.id,
                "status": {
                    "selfDeclaredMadeForKids": use_existing(channel.self_declared_made_for_kids, made_for_kids),
                },
            },
        ]
        localisations_mapping = [
            {
                "id": channel.id,
                "localizations": {
                    local_name.language: {
                        "title": local_name.title,
                        "description": local_name.description
                    } for local_name in use_existing(channel.localisations, localisations) if local_name.language
                } if use_existing(channel.localisations, localisations) else {}
            }
        ]
        contains_branding_settings = any([
            country is not EXISTING,
            description is not EXISTING,
            default_language is not EXISTING,
            keywords is not EXISTING,
            tracking_analytics_account_id is not EXISTING,
            unsubscribed_trailer is not EXISTING,
        ])
        edit_mappings = (
            (branding_settings_mapping if contains_branding_settings else [])
            +
            (made_for_kids_mapping if made_for_kids is not EXISTING else [])
            +
            (localisations_mapping if localisations is not EXISTING else [])
        )
        new_metadata = {}
        other_data = (channel.call_url, self)
        for edit_mapping in edit_mappings:
            part = await self._update_api(
                "channels", "id", channel.id, [list(edit_mapping.keys())[1]],
                lambda metadata, call_url, call_data: (metadata, call_url, call_data),
                edit_mapping, ChannelNotFound, None,
            )
            new_metadata.update(part[0])
            other_data = part[1:]
        updated_metadata = channel.metadata.copy()
        if new_metadata.get("brandingSettings") and new_metadata["brandingSettings"].get("channel"):
            updated_metadata["brandingSettings"]["channel"].update(
                ensure_missing_keys(
                    branding_settings_mapping[0]["brandingSettings"]["channel"],
                    new_metadata["brandingSettings"]["channel"]
                )
            )
            updated_metadata["snippet"].update({
                "country": new_metadata["brandingSettings"]["channel"].get("country"),
                "description": new_metadata["brandingSettings"]["channel"].get("description"),
                "defaultLanguage": new_metadata["brandingSettings"]["channel"].get("defaultLanguage")
            })
        if new_metadata.get("status"):
            updated_metadata["status"].update(
                ensure_missing_keys(made_for_kids_mapping[0]["status"], new_metadata["status"])
            )
        if new_metadata.get("localizations"):
            new_version = ensure_missing_keys(localisations_mapping[0]["localizations"], new_metadata["localizations"])
            updated_metadata["localizations"].update(
                new_version
            )
            for key in updated_metadata["localizations"].copy():
                if key not in new_version:
                    del updated_metadata["localizations"][key]
        return YoutubeChannel(updated_metadata, other_data[0], other_data[1])

    # noinspection PyIncorrectDocstring
    async def set_channel_banner(
            self, channel: YoutubeChannel, image: bytes, _auth_retry=False
    ) -> tuple[YoutubeBanner, str]:
        """
        Upload and set the banner for a channel.

        .. versionadded:: 0.4.0

        .. admonition:: Quota Impact

            A call to this method has a quota cost of **100** units per call.

        Args:
            channel (YoutubeChannel): The channel to set the banner of.
            image (bytes): The banner image to upload.

                Note:
                    The image must have a 16:9 aspect ratio and be at least 2048x1152 pixels. YouTube recommends
                    uploading a 2560px by 1440px image.

            _auth_retry (bool): Is the function being run again with new credentials. Defaults to ``False``.

        Returns:
            tuple[YoutubeBanner, str]: The metadata of the uploaded banner and the etag of the updated YoutubeChannel
            instance.

        Raises:
            HTTPException: Uploading the banner failed.
            ResourceNotFound: The API didn't return any banner or channel metadata.
            aiohttp.ClientError: There was a problem sending the request to the API.
            APITimeout: The YouTube API did not respond within the timeout period set.
        """
        if self.session and self.session.is_expired() and (not _auth_retry):
            await self.refresh_session()
            return await self.set_channel_banner(channel, image, True)
        supported_formats = {
            "png": b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',
            "jpeg": b'\xFF\xD8\xFF'
        }
        content_type = "application/octet-stream"
        for format_name, signature in supported_formats.items():
            if image.startswith(signature):
                content_type = f"image/{format_name}"
        async with aiohttp.ClientSession(
                connector=TCPConnector(verify_ssl=not self.ignore_ssl), timeout=self.timeout
        ) as session:
            headers = {
                "Authorization": f"{self.session.token_type if self.session else 'Bearer'} {self._token}",
                "Content-Type": content_type,
                "Content-Length": str(len(image))
            }
            try:
                async with session.post(
                    f"https://www.googleapis.com/upload/youtube/v{self.api_version}/channelBanners/insert"
                    f"?uploadType=media", headers=headers, data=image
                ) as response:
                    self.quota_usage += 50
                    if response.ok:
                        res_data = await response.json()
                        if "error" in res_data:
                            raise HTTPException(
                                response, f'{res_data["error"].get("code")}: {res_data["error"].get("message")}')
                        if not res_data:
                            raise ResourceNotFound("The API didn't return any thumbnail metadata")
                        else:
                            banner_url = res_data.get("url")
                    else:
                        message = f'The youtube API returned the following error code: ' \
                                  f'{response.status}'
                        error_data = None
                        if response.content_type == "application/json":
                            res_data = await response.json()
                            if "error" in res_data:
                                error_data = res_data["error"]
                                error_reasons = [error.get("reason") for error in error_data["errors"] if error]
                                if "authError" in error_reasons and self.session and (not _auth_retry):
                                    await self.refresh_session()
                                    return await self.set_channel_banner(channel, image, True)
                                message = error_data.get("message")
                        raise HTTPException(response, message, error_data)
            except asyncio.TimeoutError:
                raise APITimeout(self.timeout)
        edit_mapping = {
            "id": channel.id,
            "brandingSettings": {
                "image": {
                    "bannerExternalUrl": banner_url
                },
                "channel": {
                    "country": channel.country,
                    "description": channel.description,
                    "defaultLanguage": channel.default_language,
                    "keywords": " ".join(
                        [
                            f"\"{keyword}\"" if " " in keyword else keyword
                            for keyword in channel.keywords or []
                        ]
                    ),
                    "trackingAnalyticsAccountId": channel.tracking_analytics_account_id,
                    "unsubscribedTrailer": channel.unsubscribed_trailer_id,
                }
            }
        }
        partial = await self._update_api(
            "channels", "id", channel.id, ["brandingSettings"],
            lambda metadata, call_url, call_data: (metadata, call_url, call_data),
            edit_mapping, ChannelNotFound, None,
        )
        return YoutubeBanner(partial[0]["brandingSettings"]["image"]["bannerExternalUrl"], self), partial[0].get("etag")
