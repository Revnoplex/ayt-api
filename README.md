# ayt-api
An Asynchronous, Object oriented python library for the YouTube api

## What makes ayt-api different?
The diffrence with this library and other libraries is that it uses 
asynchronous api calls and responces are formatted as object oriented data. 

The library is also designed towards being used in discord bots, particularly ones using the discord.py library and forks of it

## Installation

ayt-api is currently not published on pypi yet, but can be installed directly from here

### Windows:
```powershell
python -m pip install -U "git+https://github.com/Revnoplex/ayt-api.git"
```

To update to the latest commit (eg. to fix a major bug) use:
```powershell
python -m pip install -U --force-reinstall "git+https://github.com/Revnoplex/ayt-api.git"
```

 

### Linux and Mac os:
```bash
pip3 install -U git+https://github.com/Revnoplex/ayt-api.git
````


To update to the latest commit (eg. to fix a major bug) use:
```bash
pip3 install -U --force-reinstall git+https://github.com/Revnoplex/ayt-api.git
```


## Basic Examples:

### Basic video snippet data fetching
```python
import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeAPI("Your API Key")


async def vid_example():
    video_data = await api.get_video_snippet_metadata("Video ID")
    print(video_data.id)
    print(video_data.channel_id)
    print(video_data.url)
    print(video_data.title)
    print(video_data.thumbnails.default.url)

loop = asyncio.new_event_loop()
loop.run_until_complete(vid_example())
```
