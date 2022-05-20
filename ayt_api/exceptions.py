import aiohttp


class YoutubeExceptions(BaseException):
    """Base exception for errors regarding the YouTube API"""
    pass


class ResourceNotFound(YoutubeExceptions):
    """Base exceptions for errors relating to a missing YouTube resource"""
    pass


class MediaNotFound(ResourceNotFound):
    """Raises if an invalid url is passed into :class:`YTDLSource.from_url()`"""
    def __init__(self, query: str):
        self.return_res = f'{query}'
        message = f'failed to return a result for "{query}". It might be an invalid input.'
        super().__init__(message)


class NoResultsFound(ResourceNotFound):
    """Raises if no search results are found when searching for the specified video in :class:`YTDLSource`.from_url()"""
    def __init__(self, query):
        self.return_res = f'{query}'
        message = f'"{query}" did not match any video results on youtube'
        super().__init__(message)

        
class PlaylistNotFound(ResourceNotFound):
    """Raises if the specified playlist id does not exist on YouTube"""
    def __init__(self, playlist_id):
        self.playlist_id = playlist_id
        message = f'The playlist id {playlist_id} did not match any visible playlists on youtube'
        super().__init__(message)


class VideoNotFound(ResourceNotFound):
    """Raises if the specified video id does not exist on YouTube"""
    def __init__(self, video_id):
        self.video_id = video_id
        message = f'The video id {video_id} did not match any visible videos on youtube'
        super().__init__(message)


class InvalidMetadata(YoutubeExceptions):
    def __init__(self, metadata: dict, message=f'The the data in the dictionary provided is invalid'):
        self.metadata = metadata
        super().__init__(message)


class MissingDataFromMetadata(InvalidMetadata):
    def __init__(self, missing_data: str, metadata: dict, exception: Exception):
        self.raw_exception = exception
        self.missing_data = missing_data
        message = f'The provided metadata object is missing data for {missing_data}'
        super().__init__(metadata, message)


class InvalidInput(YoutubeExceptions):
    """Raises if an argument in a function is invalid or empty"""
    def __init__(self, invalid_input):
        self.input = invalid_input
        message = f'{self.input}'
        if len(self.input) < 1:
            message = 'No input was provided'
        super().__init__(message)


class HTTPException(YoutubeExceptions):
    """Exception that's raised when an HTTP request operation fails."""

    def __init__(self, response: aiohttp.ClientResponse, message: str = None):
        self.response: aiohttp.ClientResponse = response
        self.status: int = response.status  # type: ignore
        self.text: str
        self.text = f': {message}' or ""

        super().__init__(f'{self.response.status} {self.response.reason}{self.text}')
