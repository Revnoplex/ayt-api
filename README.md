![PyPI](https://img.shields.io/pypi/v/ayt-api?style=for-the-badge&logo=pypi)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ayt-api?style=for-the-badge&logo=python)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/Revnoplex/ayt-api?style=for-the-badge&logo=github)
![PyPI - Downloads per month](https://img.shields.io/pypi/dm/ayt-api?style=for-the-badge&logo=pypi)
![Supported Python Versions](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FRevnoplex%2Fayt-api%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&style=for-the-badge&logo=python)
![Repo Created At](https://img.shields.io/github/created-at/Revnoplex/ayt-api?style=for-the-badge)
# ayt-api
A Basic, Asynchronous, Object-Oriented YouTube API Wrapper Written in Python.

The library is designed towards being used in python based discord bots that use an asynchronous discord api wrapper

## Installation

### Stable Release:
The latest stable version is available on pypi
#### Windows:
```powershell
python -m pip install -U ayt-api
```

#### Unix based OSes (Linux, Mac OS, etc.):
The pip command can vary between different unix based OSes but should be simular to these:
```sh
python3 -m pip install -U ayt-api

# or

pip3 install -U ayt-api
```

### Latest Commit:
Installing the latest commit from here. You will need git or something simular installed to download the library
#### Windows:
```powershell
python -m pip install -U "git+https://github.com/Revnoplex/ayt-api.git"
```

#### Unix based OSes (Linux, Mac OS, etc.):
The pip command can vary between diffrent unix based OSes but should be simular to these:
```sh
python3 -m pip install -U git+https://github.com/Revnoplex/ayt-api.git

# or

pip3 install -U git+https://github.com/Revnoplex/ayt-api.git
```

## Usage
First of all to use this library, you will need an API key. To get one, [see here for instructions](https://developers.google.com/youtube/v3/getting-started)

### Basic video data fetching:
```python
import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeAPI("Your API Key")


async def video_example():
    video_data = await api.fetch_video("Video ID")
    print(video_data.id)
    print(video_data.channel_id)
    print(video_data.url)
    print(video_data.title)
    print(video_data.thumbnails.default.url)
    print(video_data.visibility)
    print(video_data.duration)
    print(video_data.view_count)
    print(video_data.like_count)
    print(video_data.embed_html)
    print(video_data.published_at)
    print(video_data.description)
    print(video_data.age_restricted)

loop = asyncio.new_event_loop()
loop.run_until_complete(video_example())
```

### Basic playlist data fetching:
```python
import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeAPI("Your API Key")


async def playlist_example():
    playlist_data = await api.fetch_playlist("Playlist ID")
    print(playlist_data.id)
    print(playlist_data.channel_id)
    print(playlist_data.url)
    print(playlist_data.title)
    print(playlist_data.thumbnails.default.url)
    print(playlist_data.visibility)
    print(playlist_data.published_at)
    print(playlist_data.description)
    print(playlist_data.embed_html)
    print(playlist_data.item_count)

loop = asyncio.new_event_loop()
loop.run_until_complete(playlist_example())
```

### Basic playlist video fetching:
```python
import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeAPI("Your API Key")


async def playlist_video_example():
    playlist_videos = await api.fetch_playlist_videos("Playlist ID")
    video = playlist_videos[0]
    print(video.id)
    print(video.channel_id)
    print(video.url)
    print(video.title)
    print(video.thumbnails.default.url)
    print(video.visibility)
    print(video.published_at)
    print(video.description)
    print(video.duration)

loop = asyncio.new_event_loop()
loop.run_until_complete(playlist_video_example())
```

More examples are listed [here](https://github.com/Revnoplex/ayt-api/tree/main/examples)
