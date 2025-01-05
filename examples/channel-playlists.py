import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeAPI("Your API Key")


async def channel_playlists_example():
    channel = await api.fetch_channel_from_handle("@your_channel_handle")
    playlists = await channel.fetch_playlists()
    print([playlist.title for playlist in playlists])

asyncio.run(channel_playlists_example())
