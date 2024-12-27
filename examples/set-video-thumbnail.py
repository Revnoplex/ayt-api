import ayt_api
import asyncio


async def set_video_thumbnail_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret"
    )
    video = await api.fetch_video(f"Video ID", authorised=True)
    print(video.thumbnails.highest.url)
    print(video.thumbnails.highest.resolution)
    print(video.thumbnails.etag)
    with open("Your Thumbnail File", 'rb') as image_f:
        image = image_f.read()
    await video.set_thumbnail(image)
    # Note: This replaces the files at https://i.ytimg.com/vi/Video_ID/Image_Quality.jpg so the url doesn't change.
    print(video.thumbnails.highest.url)
    print(video.thumbnails.highest.resolution)
    print(video.thumbnails.etag)


asyncio.run(set_video_thumbnail_example())
