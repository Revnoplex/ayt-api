import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeAPI("Your API Key")


async def video_captions_example():
    captions = await api.fetch_video_captions("Video ID")
    print(captions[0].video_id)
    print(captions[0].language)
    print(captions[0].is_cc)

loop = asyncio.new_event_loop()
loop.run_until_complete(video_captions_example())
