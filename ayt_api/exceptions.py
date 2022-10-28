import aiohttp


class YoutubeExceptions(BaseException):
    """Base exception for errors regarding the YouTube API."""
    pass


class ResourceNotFound(YoutubeExceptions):
    """Base exceptions for errors relating to a missing YouTube resource."""
    pass


class PlaylistNotFound(ResourceNotFound):
    """Raises if the specified playlist id does not exist on YouTube.
    Args:
        playlist_id (str): playlist id that was attempted to be fetched
    Attributes:
        playlist_id (str): playlist id that was attempted to be fetched
    """
    def __init__(self, playlist_id):
        self.playlist_id = playlist_id
        message = f'The playlist id {playlist_id} did not match any visible playlists on youtube'
        super().__init__(message)


class VideoNotFound(ResourceNotFound):
    """Raises if the specified video id does not exist on YouTube.
    Args:
        video_id (str): video id that was attempted to be fetched
    Attributes:
        video_id (str): video id that was attempted to be fetched
    """
    def __init__(self, video_id):
        self.video_id = video_id
        message = f'The video id {video_id} did not match any visible videos on youtube'
        super().__init__(message)


class InvalidMetadata(YoutubeExceptions):
    """Raises when invalid metadata is given.
    Args:
        metadata (dict): The raw data that is invalid
        message (str): The error message to send along with the exception
    Attributes:
        metadata (dict): The raw data that is invalid
    """
    def __init__(self, metadata: dict, message=f'The the data in the dictionary provided is invalid'):
        self.metadata = metadata
        super().__init__(message)


class MissingDataFromMetadata(InvalidMetadata):
    """Raises when the metadata in the response is malformed.
    Args:
        missing_data (str):
            The error message to send along with the exception
        metadata (dict): The raw payload data that is malformed
        exception (Exception): The original exception raised to trigger this exception
    Attributes:
        raw_exception (Exception): The original exception raised to trigger this exception
        missing_data (str): The error message to send along with the exception
    """
    def __init__(self, missing_data: str, metadata: dict, exception: Exception):
        self.raw_exception = exception
        self.missing_data = missing_data
        message = f'The provided metadata object is missing data for {missing_data}. This is most likely be a bug so ' \
                  f'please report this error on the github (https://github.com/Revnoplex/ayt-api) and make sure to ' \
                  f'include the id of the video/playlist and the entirety of this traceback'
        super().__init__(metadata, message)


class InvalidInput(YoutubeExceptions):
    """Raises if an argument in a function is invalid or empty.
    Args:
        invalid_input (Any): The invalid input that was provided
    Attributes:
        input (Any): The invalid input that was provided
    """
    def __init__(self, invalid_input):
        self.input = invalid_input
        message = f'{self.input}'
        if len(self.input) < 1:
            message = 'No input was provided'
        super().__init__(message)


class InvalidKey(YoutubeExceptions):
    """Exception that's raised when an invalid API key is passed"""
    def __init__(self):
        super().__init__("API key not valid. Please pass a valid API key.")


class APITimeout(YoutubeExceptions):
    """Exception that's raised when the api does not respond within the timeout set
    Attributes:
        timeout_set (int): The timeout that was set
    """
    def __init__(self, timeout_set: aiohttp.ClientTimeout):
        """
        Args:
            timeout_set (int): The timeout that was set
        """
        self.timeout_set = timeout_set.total
        super().__init__("The Youtube API is not responding")


class HTTPException(YoutubeExceptions):
    """Exception that's raised when an HTTP request operation fails.
    Args:
        response (ClientResponse): The aiohttp response associated with the error
        message (str): The error message associated with the error that the YouTube api gave
        error_data (dict): The raw error data associated with the error
    Attributes:
        response (ClientResponse): The aiohttp response associated with the error
        message (str): The error message associated with the error that the YouTube api gave
        status (int): The HTTP status code associated with the error
        error_data (dict): The raw error data associated with the error
        """
    def __init__(self, response: aiohttp.ClientResponse, message: str = None, error_data: dict = None):
        self.response: aiohttp.ClientResponse = response
        self.error_data = error_data
        self.details = error_data.get("details")
        if self.details is not None:
            self.reason = self.details[0].get("reason")
        else:
            self.reason = error_data["errors"][0].get("reason")
        self.status: int = response.status
        self.message = message
        if self.reason == "API_KEY_INVALID":
            raise InvalidKey()
        self.text: str = f': {message}' or ""
        super().__init__(f'{self.response.status} {self.response.reason}{self.text}')
