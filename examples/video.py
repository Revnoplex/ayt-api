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

asyncio.run(video_example())
