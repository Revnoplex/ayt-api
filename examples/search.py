import asyncio
import ayt_api
from ayt_api.types import YoutubeChannel

api = ayt_api.AsyncYoutubeAPI("Your API Key")


async def search_example():
    search_result = await api.search("Channel Name", 10, ayt_api.SearchFilter(_type=YoutubeChannel))
    print(len(search_result))
    for result in search_result:
        print(result.call_url)
        print(result.kind_id)
        print(result.kind)
        print(result.url)
        print(result.title)
        print(result.channel_title)
        print(result.live_broadcast_content)
        print(result.thumbnails.default)

loop = asyncio.new_event_loop()
loop.run_until_complete(search_example())
