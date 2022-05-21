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
