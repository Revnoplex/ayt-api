import ayt_api
import asyncio


async def oauth2_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret"
    )
    resource = await api.fetch_video("Video ID", True)
    print(resource.file_name)


asyncio.run(oauth2_example())
