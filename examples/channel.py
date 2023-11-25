import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeApi("Your API Key")


async def channel_example():
    channel = await api.fetch_channel("Channel ID")
    print(channel.call_url)
    print(channel.thumbnails)
    print(channel.localised)
    print(channel.related_playlists)
    print(channel.long_upload_status)
    print(channel.keywords)
    print(channel.banner_external_url)
    print(channel.url)

loop = asyncio.new_event_loop()
loop.run_until_complete(channel_example())