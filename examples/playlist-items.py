import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeApi("Your API Key")


async def playlist_video_example():
    playlist_videos = await api.fetch_playlist_items("Playlist ID")
    video_data = playlist_videos[0]
    print(video_data.id)
    print(video_data.channel_id)
    print(video_data.url)
    print(video_data.title)
    print(video_data.thumbnails.default.url)
    print(video_data.visibility)
    print(video_data.published_at)
    print(video_data.description)
    print(video_data.playlist_url)
    print(video_data.added_at)

loop = asyncio.new_event_loop()
loop.run_until_complete(playlist_video_example())
