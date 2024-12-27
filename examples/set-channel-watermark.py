import datetime

import ayt_api
import asyncio


async def set_channel_watermark_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret"
    )
    channel = await api.fetch_channel_from_handle("@your_channel_handle")
    with open("Your Watermark File", "rb") as watermark_file:
        watermark = watermark_file.read()
    await channel.set_watermark(
        watermark, ayt_api.WatermarkTimingType.offset_from_start, datetime.timedelta(seconds=2),
        datetime.timedelta(seconds=10)
    )


asyncio.run(set_channel_watermark_example())
