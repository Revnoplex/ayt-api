import ayt_api
import asyncio


async def user_channel_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret"
    )
    channel = await api.fetch_user_channel()
    print(channel.title)
    print(channel.handle)


asyncio.run(user_channel_example())
