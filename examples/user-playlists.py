import ayt_api
import asyncio


async def user_playlists_example():
    consent_url, sock = ayt_api.AsyncYoutubeAPI.generate_url_and_socket(
        "Your Client ID"
    )
    print(consent_url)
    api = await ayt_api.AsyncYoutubeAPI.with_authcode_receiver(
        consent_url, sock, "Your Client Secret"
    )
    playlists = await api.fetch_user_playlists()
    print([playlist.title for playlist in playlists])


asyncio.run(user_playlists_example())
