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
        missing_data (str): The error message to send along with the exception
        metadata (dict): The raw payload data that is malformed
        exception (Exception): The original exception raised to trigger this exception
    Attributes:
        raw_exception (Exception): The original exception raised to trigger this exception
        missing_data (str): The error message to send along with the exception
    """
    def __init__(self, missing_data: str, metadata: dict, exception: Exception):
        self.raw_exception = exception
        self.missing_data = missing_data
        message = f'The provided metadata object is missing data for {missing_data}'
        super().__init__(metadata, message)


class InvalidInput(YoutubeExceptions):
    """Raises if an argument in a function is invalid or empty.
    Args:
        invalid_input (Any): The invalid input that was provided
    Attributes:
        invalid_input (Any): The invalid input that was provided
    """
    def __init__(self, invalid_input):
        self.input = invalid_input
        message = f'{self.input}'
        if len(self.input) < 1:
            message = 'No input was provided'
        super().__init__(message)


class HTTPException(YoutubeExceptions):
    """Exception that's raised when an HTTP request operation fails.
    Args:
        response (ClientResponse): The aiohttp response associated with the error
        message (str): The error message associated with the error that the YouTube api gave
    Attributes:
        response (ClientResponse): The aiohttp response associated with the error
        message (str): The error message associated with the error that the YouTube api gave
        status (int): The HTTP status code associated with the error
        """

    def __init__(self, response: aiohttp.ClientResponse, message: str = None):
        self.response: aiohttp.ClientResponse = response
        self.status: int = response.status
        self.message = message
        self.text: str = f': {message}' or ""

        super().__init__(f'{self.response.status} {self.response.reason}{self.text}')
