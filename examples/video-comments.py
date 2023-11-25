import asyncio
import ayt_api

api = ayt_api.AsyncYoutubeAPI("Your API Key")


async def video_comments_example():
    video_comments_data = await api.fetch_video_comments("Video ID")
    print(video_comments_data[0].top_level_comment.video_id)
    print(video_comments_data[0].top_level_comment.author_display_name)
    print(video_comments_data[0].top_level_comment.text_original)
    print(video_comments_data[0].top_level_comment.id)
    print(video_comments_data[0].highlight_url)
    print(len(video_comments_data))
    print(video_comments_data[0].call_url)

loop = asyncio.new_event_loop()
loop.run_until_complete(video_comments_example())

