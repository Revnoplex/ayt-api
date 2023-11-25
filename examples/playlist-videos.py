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
