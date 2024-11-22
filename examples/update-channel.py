import ayt_api
import asyncio


async def update_channel_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret"
    )
    original_channel = await api.fetch_channel_from_handle("@your_channel_handle")
    print(original_channel.description)
    updated_channel = await original_channel.update(
        description="New Description"
    )
    print(updated_channel.description)


asyncio.run(update_channel_example())
