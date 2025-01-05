import ayt_api
import asyncio


async def update_playlist_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret"
    )
    original_playlist = await api.fetch_playlist("Your Playlist ID")
    print(original_playlist.title)
    updated_playlist = await original_playlist.update(description="New Title")
    print(updated_playlist.title)


asyncio.run(update_playlist_example())
