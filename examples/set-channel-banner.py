import ayt_api
import asyncio


async def set_channel_banner_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret", timeout=10
    )
    channel = await api.fetch_channel_from_handle("@your_channel_handle")
    print(channel.etag)
    print(channel.banner_external.url)
    with open("Your Banner File", "rb") as banner_file:
        banner = banner_file.read()
    await channel.set_banner(banner)
    print(channel.etag)
    print(channel.banner_external.url)


asyncio.run(set_channel_banner_example())
