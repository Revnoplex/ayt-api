import ayt_api
import asyncio


async def oauth2_auth_code_example():
    api = await ayt_api.AsyncYoutubeAPI.with_authorisation_code(
        "Your Authorisation Code", "Your Client ID", "Your Client Secret", "Your Redirect URI"
    )
    resource = await api.fetch_video("Video ID", True)
    print(resource.file_name)


asyncio.run(oauth2_auth_code_example())
