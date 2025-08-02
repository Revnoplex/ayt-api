import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeAPI("Your API Key")


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

asyncio.run(playlist_video_example())
