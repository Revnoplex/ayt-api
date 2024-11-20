import ayt_api
import asyncio


async def update_video_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret"
    )
    original_video = await api.fetch_video("Video ID", authorised=True)
    print(original_video.title)
    updated_video = await original_video.update(
        title="New Title"
    )
    print(updated_video.title)


asyncio.run(update_video_example())
