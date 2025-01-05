import ayt_api
import asyncio


async def update_playlist_item_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret"
    )
    items = await api.fetch_playlist_items("Your Playlist ID")
    print(items[0].position)
    updated_item = await items[0].update(position=1)
    print(updated_item.position)


asyncio.run(update_playlist_item_example())
