import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeAPI("Your API Key")


async def playlist_example():
    playlist_data = await api.get_playlist_metadata("Playlist ID")
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
