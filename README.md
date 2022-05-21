# ayt-api
An Asynchronous, Object oriented python library for the YouTube api


## Installation

ayt-api is currently not published on pypi yet, but can be installed directly from here

### Windows:
```powershell
python -m pip install -U git+https://github.com/Revnoplex/ayt-api.git
```

### Linux and Mac os:
```bash
pip3 install -U git+https://github.com/Revnoplex/ayt-api.git
```


## Basic Examples:

### Basic video snippet data fetching
```python
import asyncio
from ayt_api import async_youtube_api

api = async_youtube_api.AsyncYoutubeAPI("Your API Key")


async def example():
    video_data = await api.get_video_snippet_metadata("Video ID")
    print(video_data.id)
    print(video_data.channel_id)
    print(video_data.url)
    print(video_data.title)
    print(video_data.thumbnails.default.url)

loop = asyncio.new_event_loop()
loop.run_until_complete(example())
```
